from bs4 import BeautifulSoup
from bs4.element import Comment
from hashlib import sha256
from typing import Iterable

def tokenize(input_str: str) -> list[str]:
    """File Tokenizer

    Args:
        input_str (str): str to tokenize

    Returns:
        list[str]: a list of the tokens in the input
    """
    
    tokens = []
    
    tok = ""
    # iterate through chars in the line
    for c in input_str.lower():
        # if c is alphanumeric add to token
        if c.isalnum():
            tok += c
        # if c is not alphanumeric and tok holds a token,
        # add tok to the tokens list
        elif len(tok) > 0:
            tokens.append(tok)
            tok = ""
    # add a token left in tok when the line ends to the token list
    if len(tok) > 0:
        tokens.append(tok)
    
    return tokens

def computeWordFrequencies(tokens: list[str]) -> dict[str:int]:
    """Computes the frequencies of each token in the tokens list

    Args:
        tokens (list[str]): the list of string tokens

    Returns:
        dict[str:int]: the dictionary containing (token: frequency) items
    """
    
    freq = {}
    for tok in tokens:
        # for each token, set the value in the freq dict to
        # the current value (default 0) plus 1
        freq[tok] = freq.get(tok, 0) + 1
    return freq

def tag_visible(element):
    if element.parent.name in ["style", "script", "head", "title", "meta", "[document]"]:
        return False
    if isinstance(element, Comment):
        return False
    return True

def to_tokens(htmlContent: str) -> list[str]:
    soup = BeautifulSoup(htmlContent, "lxml")
    texts = [t for t in soup.findAll(text = True) if tag_visible(t)]
    tokens = [tok for t in texts for tok in tokenize(t)]
    return tokens

def ngrams(tokens: str, n: int = 3) -> Iterable[tuple[str]]:
    return zip(*[tokens[i:] for i in range(n)])

def hash(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()

def fingerprint(tokens: list[str], q: int = 4) -> set[str]:
    """Create a Fingerprint for the text represented by the given token list
    
    Args:
        tokens (list[str]): the list of tokens
        q (int): optional. Modulo parameter for hash subset selection. Defaults to 4.
    
    Returns:
        str: the hex fingerprint set
    """
    return set(h for h in [hash(" ".join(t)) for t in ngrams(tokens)] if int(h, 16) % q == 0)

def mergeDicts(x: dict[str: int], y: dict[str: int]) -> dict[str: int]:
    return {k: x.get(k, 0) + y.get(k, 0) for k in set(x) | set(y)}

def similarity(x: set[str], y: set[str]) -> float:
    return len(x.intersection(y)) / len(x.union(y))