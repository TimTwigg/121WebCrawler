# This is a testing file I'm using to develop and test functions
# jellyfish is not a built-in library. It is for string similarity comparison

# TODO
# implement list_similarity

import jellyfish

# textual simlarity
def similarity(a: str, b: str) -> float:
    return jellyfish.jaro_winkler_similarity(a, b)

# similarity in token lists
# return a float between 0 and 1 which represents the similarity percentage
def list_similarity(l1: list[str], l2: list[str]) -> float:
    pass

# repeated patterns
def repeats(url: str) -> int:
    pieces = url.split("/")
    return len(pieces) - len(set(pieces))

if __name__ == "__main__":
    pass