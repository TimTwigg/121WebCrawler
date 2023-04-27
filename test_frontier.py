import crawler.frontier
import random


# Gets the top 50 words and their counts
# Returns a dictionary containing those top 50 words
# dict(token: count)
def get_top_50_words(bank) -> dict():
    counts = dict()

    for url, page_dict in bank.items():
        for token, count in page_dict.items():
            if token not in counts:
                counts[token] = count
            else:
                counts[token] += count

    sorted_dict = dict()


    # Iterates over the first 50 tokens, adds them to new dict
    for token, count in sorted(counts.items(), key=lambda x: -x[1])[:50]:
        sorted_dict[token] = count

    return sorted_dict

test_tokens = dict()

for page_idx in range(10):
    for token_idx in range(100):
        count = random.randint(1,1000)
        if f"{page_idx}" not in test_tokens:
            test_tokens[f"{page_idx}"] = dict()

        test_tokens[f"{page_idx}"][f"{token_idx}"] = count

# for key in test_tokens:
# print(test_tokens)
print(get_top_50_words(test_tokens))