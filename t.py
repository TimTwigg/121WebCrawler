import jellyfish

# textual simlarity
def similarity(a: str, b: str) -> float:
    return jellyfish.jaro_winkler_similarity(a, b)

# repeated patterns
def repeats(url: str) -> int:
    pieces = url.split("/")
    return len(pieces) - len(set(pieces))

if __name__ == "__main__":
    s1 = "https://www.stat.uci.edu/slider/uci-launches-new-professional-program-master-of-data-science"
    s2 = "http://www.ics.uci.edu/ugrad/ugrad"
    s3 = "http://www.ics.uci.edu/ugrad/ugrad/ugrad/ugrad/hel"
    l1 = ["a", "b", "c"]
    l2 = ["a", "c", "d"]
    # print(repeats(s1), repeats(s2), repeats(s3), sep = "\n")
    # print(similarity(l1, l2))