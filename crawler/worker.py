from threading import Thread
from urllib.parse import urlparse

from inspect import getsource
from urllib.parse import urlparse

from utils.download import download
from utils import get_logger, get_urlhash
import scraper
import time
from helpers import to_tokens, fingerprint, computeWordFrequencies, mergeDicts

class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier

        self.last_time = -1

        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break

            # self.logger.info(f"About to download {tbd_url}")
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")

            if resp and resp.raw_response and resp.raw_response.content:
                # Bigger than 10MB webpage
                if len(resp.raw_response.content) > 10000000:
                    self.logger.info(f"URL {tbd_url} too big")
                    self.handle_bad_url(tbd_url)
            elif resp.raw_response == None:
                # Spacetime error
                self.handle_bad_url(tbd_url)
                continue
            
            # added code to keep track of info about scraped pages
            ########################################################
            # Handle redirects

            # Special custom case
            # Means that requests.get failed and need to retry url
            if resp.status == -1:
                urlhash = get_urlhash(tbd_url)
                del self.frontier.save[urlhash]
                self.frontier.add_url(tbd_url)
                self.sleep_until_next_crawl()
                continue
            if 300 <= resp.status <= 399:
                # https://stackoverflow.com/a/50606372
                # resp.url should be the url from the redirect
                # Add it to the frontier
                self.logger.info("Redirect: tbd_url, resp.url")
                self.frontier.add_url(resp.url)
                self.handle_bad_url(tbd_url)
                continue
            elif resp.status == 404:
                self.handle_bad_url(tbd_url)
                self.frontier.not_found_count += 1
                continue
            # Catch bad status
            elif resp.status != 200:
                self.handle_bad_url(tbd_url)
                continue
            
            tokens = to_tokens(resp.raw_response.content)
            
            # add tokens to tokens count dict
            self.frontier.tokens = mergeDicts(self.frontier.tokens, computeWordFrequencies(tokens))
            
            # update longest site
            if len(tokens) > self.frontier.longestSiteLength:
                self.frontier.longestSiteLength = len(tokens)
                self.frontier.longestSiteURL = tbd_url

            self.logger.info(f"Token Count: {len(tokens)}")
            self.logger.info(f"Response length: {len(resp.raw_response.content)}")
            
            # track ics.uci.edu subdomains
            if ".ics.uci.edu" in tbd_url:
                # Subdomains can be uniquely identified by the entire domain
                # We can use entire domain as key, no need to extract subdomain
                parsed_url = urlparse(tbd_url)
                domain = parsed_url.netloc
                self.frontier.domains[domain] = self.frontier.domains.get(domain, 0) + 1

            # self.logger.info(f"Starting similarity comparison {tbd_url}")
            # compute fingerprint and use it to compare similarity
            fp = fingerprint(tokens)
            if self.frontier.similarToBank(fp):
                # do not scrape if the content is too similar to one we've already scraped
                self.handle_bad_url(tbd_url)
                self.logger.info("too similar")
                continue

            # self.logger.info(f"Ending similarity comparison {tbd_url}")
            
            self.frontier.bank[get_urlhash(tbd_url)] = fp
            ########################################################
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            self.sleep_until_next_crawl()
        self.frontier.save_all()

    # idk what to name this functions
    # Standardized handling of bad urls
    # Mark as complete
    # Wait for politeness
    def handle_bad_url(self, url: str):
        self.frontier.mark_url_complete(url)
        self.sleep_until_next_crawl()

    def sleep_until_next_crawl(self):
        if self.last_time == -1:
            time.sleep(self.config.time_delay)
        else:
            time_diff = time.time() - self.last_time

            if 0 < time_diff < self.config.time_delay:
                time.sleep(self.config.time_delay - time_diff)

        self.last_time = time.time()