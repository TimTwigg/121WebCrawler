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

# Linearithmic Time O(nlogn) where n is the number of unique frequencies in the input dict.
# The items are sorted, and then each is examined exactly once to print.
# Sorting the items requires O(nlogn) time, printing requires O(n), thus the time complexity
# is dominated by the linearithmic sorting time.
def printFrequencies(frequencies: dict[str:int]) -> None:
    """Print the given frequencies dictionary in the format: token => frequency

    Args:
        frequencies (dict[str:int]): the frequency dictionary to be printed
    """
    
    # sort primarily by decreasing frequency and secondarily by token alphabetically
    # and then unpack into key,value pairs to print
    for (k,v) in sorted(frequencies.items(), key = lambda x: (-x[1], x[0])):
        print(f"{k} => {v}")