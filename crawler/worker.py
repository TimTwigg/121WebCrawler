from threading import Thread

from inspect import getsource
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
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            
            # added code to keep track of info about scraped pages
            ########################################################
            tokens = to_tokens(resp.raw_response.content)
            # add tokens to tokens count dict
            self.frontier.tokens = mergeDicts(self.frontier.tokens, computeWordFrequencies(tokens))
            # update longest site
            if len(tokens) > self.frontier.longestSiteLength:
                self.frontier.longestSiteLength = len(tokens)
                self.frontier.longestSiteURL = tbd_url
            # compute fingerprint and use it to compare similarity
            fp = fingerprint(tokens)
            if self.frontier.similarToBank(fp):
                # do not scrape if the content is too similar to one we've already scraped
                continue
            self.frontier.bank[get_urlhash(tbd_url)] = fp
            ########################################################
            
            scraped_urls = scraper.scraper(tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
        self.frontier.save_all()
