import re
from urllib.parse import urlparse, ParseResult
from bs4 import BeautifulSoup

URL_REPEAT_THRESH = 1

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    
    soup = BeautifulSoup(resp.raw_response.content, "lxml")
    links = set()
    for link in soup.find_all("a"):
        l = link.get("href")
        # ignore <a> tags with no href
        if l is None:
            continue
        # cut off the fragment and whitespace
        l = l.split("#")[0].strip()
        if len(l) < 1:
            continue
        
        # convert relative urls to absolute
        if is_relative(l):
            parsed_url = urlparse(url)
            parsed_relative = urlparse(l)
            l = ParseResult(scheme=parsed_url.scheme, netloc=parsed_url.netloc, path=parsed_relative.path,
                            params=parsed_relative.params, query=parsed_relative.query,
                            fragment=parsed_relative.fragment).geturl()
        
        # detect repeated segments in url
        pieces = url.split("/")
        if len(pieces) - len(set(pieces)) > URL_REPEAT_THRESH:
            continue
        
        links.add(l)
    # return list(links)
    print(f"Found: {len(links)}")
    return list(links)[:1]

def is_relative(url):
    return urlparse(url).scheme == ""

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)

        # Checks if any of the valid domains is in URL
        # Returns False if url doesn't contain them
        valid_domains = [".ics.uci.edu/", ".cs.uci.edu/", ".informatics.uci.edu/", ".stat.uci.edu/"]
        if all(domain not in url for domain in valid_domains):
            # print(url)
            return False
        
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise