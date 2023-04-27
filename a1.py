from bs4 import BeautifulSoup
from bs4.element import Comment

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

def to_tokens(htmlContent: str) -> dict[str: int]:
    soup = BeautifulSoup(htmlContent)
    texts = [t for t in soup.findAll(text = True) if tag_visible(t)]
    tokens = [tok for t in texts for tok in tokenize(t)]
    return computeWordFrequencies(tokens)

def compareSiteFreqs(tokens1: list[str], tokens2: list[str]) -> float:
    """Compare the tokens in two sites for common tokens and return the percentage of commonality
    
    Args:
        tokens1 (list[str]): the first token set
        tokens2 (list[str]): the second token set
    
    Returns:
        float: the average of the percentages of each set of tokens which are common
    """
    
    common = set(tokens1).intersection(tokens2)
    return ((len(common) / len(tokens1)) + (len(common) / len(tokens2))) / 2