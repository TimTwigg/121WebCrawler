import os
import shelve
import signal
from threading import Thread, RLock
from queue import Queue, Empty
import json
import time
import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer


from helpers import similarity
from utils import get_logger, get_urlhash, normalize
from scraper import is_valid

class Frontier(object):
    def __init__(self, config, restart):
        nltk.download('stopwords')
        nltk.download('words')
        self.logger = get_logger("FRONTIER")
        self.config = config
        self.to_be_downloaded = Queue()
        self.seen_count = 0
        "The number of unique sites seen."
        self.not_found_count = 0
        "The number of 404 responses received."
        self.bank: dict[str: set[str]] = {}
        """bank has the structure: \n
                { hashedURL: hash fingerprint set }"""
        self.tokens: dict[str: int] = {}
        """tokens has the structure: \n
                { token: count }"""
        self.domains: dict[str: int] = {}
        """domains has the structure: \n
                { subdomainURL: numPages }
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
            elif completed and is_valid(url):
                self.seen_count += 1
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
        self.save_bank()

    def save_summary(self):
        top50words = "\n\t".join(f"{item[0]}: {item[1]}" for item in self.get_top_50_words())
        with open("summary.txt", "w") as f:
            info = \
f"""Total Sites Crawled: {self.seen_count}
Total Sites Crawled Excluding 404s: {self.seen_count - self.not_found_count}
Number of ics.uci.edu Subdomains Crawled: {len(self.domains)}
Longest Site URL: {self.longestSiteURL}
Length of Longest Site: {self.longestSiteLength}
Top 50 Words:
\t{top50words}
"""
            f.write(info)
    
    def save_bank(self):
        self.logger.info(f"Seen: {self.seen_count}, Bank Size: {len(self.bank)}, NotFoundCount: {self.not_found_count}")
        with open("bank.json", "w") as f:
            json.dump([{k:list(v) for k,v in self.bank.items()}, self.tokens, self.domains, self.longestSiteURL, self.longestSiteLength, self.not_found_count], f, indent = 4)
            
    def load_bank(self):
        try:
            with open("bank.json", "r") as f:
                bank, self.tokens, self.domains, self.longestSiteURL, self.longestSiteLength, self.not_found_count = json.load(f)
            self.bank = {k: set(v) for k, v in bank.items()}
        except FileNotFoundError:
            pass
    
    def save_all(self):
        self.save.sync()
        self.save_summary()
        self.save_bank()

    def get_top_50_words(self) -> list[tuple[str, int]]:
        return sorted(self.tokens.items(), key = lambda item: -1 * item[1])[:50]

    def remove_stop_words(self):
        stop_words = set(stopwords.words('english'))
        token_copy = dict(self.tokens)

        for token in token_copy:
            if token in stop_words:
                del self.tokens[token]

    def remove_non_english(self):
        valid_words = set(nltk.corpus.words.words())
        token_copy = dict(self.tokens)

        for token in token_copy:
            if token not in valid_words:
                del self.tokens[token]
            elif len(token) <= 1:
                # Remove the case where the token is a single letter
                # This is sometimes a "valid" word like 'e'
                del self.tokens[token]

    # Simplifies words to their base forms
    def stem_tokens(self):
        # https://www.nltk.org/howto/stem.html
        stemmer = SnowballStemmer('english')

        new_tokens = dict()

        for token, count in self.tokens.items():
            stemmed_token = stemmer.stem(token)

            if stemmed_token not in new_tokens:
                new_tokens[stemmed_token] = count
            else:
                new_tokens[stemmed_token] += count

        self.tokens = new_tokens

    # checks if a given fingerprint set is too similar to one in the bank
    # the similarity score is compared to a float, 0.8 means 80% similarity.
    def similarToBank(self, fprint: set[str]) -> bool:
        return any((similarity(fprint, fp) > 0.8 for fp in self.bank.values()))
