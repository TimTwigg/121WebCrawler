import os
import shelve
from threading import Thread, RLock
from queue import Queue, Empty
import json

from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

class Frontier(object):
    def __init__(self, config, restart):
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = Queue()
        self.seen_count = 0
        "The number of unique sites seen."
        self.bank: dict[str: dict[str: int]] = {}
        """bank has the structure: \n
                { hashedURL: { token: count } }"""
        self.domains: dict[str: dict[str: int]]
        """domains has the structure: \n
                { domainURL: { subdomainURL: numPages } }
        """
        self.longestSiteURL = None
        self.longestSiteLength = 0
        
        if not os.path.exists(self.config.save_file) and not restart:
            # Save file does not exist, but request to load save.
            self.logger.info(
                f"Did not find save file {self.config.save_file}, "
                f"starting from seed.")
        elif os.path.exists(self.config.save_file) and restart:
            # Save file does exists, but request to start from seed.
            self.logger.info(
                f"Found save file {self.config.save_file}, deleting it.")
            os.remove(self.config.save_file)
        # Load existing save file, or create one if it does not exist.
        self.save = shelve.open(self.config.save_file)
        if restart:
            for url in self.config.seed_urls:
                self.add_url(url)
        else:
            # Set the frontier state with contents of save file.
            self._parse_save_file()
            if not self.save:
                for url in self.config.seed_urls:
                    self.add_url(url)
            self.load_bank()

    def _parse_save_file(self):
        ''' This function can be overridden for alternate saving techniques. '''
        total_count = len(self.save)
        tbd_count = 0
        for url, completed in self.save.values():
            if not completed and is_valid(url):
                self.to_be_downloaded.put(url)
                tbd_count += 1
        self.logger.info(
            f"Found {tbd_count} urls to be downloaded from {total_count} "
            f"total urls discovered.")

    def get_tbd_url(self):
        try:
            return self.to_be_downloaded.get(False)
        except IndexError:
            return None
        except Empty:
            return None

    def add_url(self, url):
        url = normalize(url)
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            self.save[urlhash] = (url, False)
            self.save.sync()
            self.to_be_downloaded.put(url)
    
    def mark_url_complete(self, url):
        urlhash = get_urlhash(url)
        if urlhash not in self.save:
            # This should not happen.
            self.logger.error(
                f"Completed url {url}, but have not seen it before.")

        self.save[urlhash] = (url, True)
        self.seen_count += 1
        self.save.sync()

    def save_summary(self):
        with open("summary.txt", "w") as f:
            info = f"""
            Total Sites Crawled: {self.seen_count}
            Number of Domains Crawled: {len(self.domains)}
            Longest Site URL: {self.longestSiteURL}
            Length of Longest Site: {self.longestSiteLength}
            """
            f.write(info)
    
    def save_bank(self):
        with open("bank.json", "w") as f:
            json.dump([self.bank, self.domains, self.longestSiteURL, self.longestSiteLength], f)
            
    def load_bank(self):
        try:
            with open("bank.json", "r") as f:
                self.bank, self.domains, self.longestSiteURL, self.longestSiteLength = json.load(f)
        except FileNotFoundError:
            pass
    
    def save_all(self):
        self.save.sync()
        self.save_summary()
        self.save_bank()