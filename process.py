import json

with open("stop_words.txt", "r") as f:
    stop_words = [l.strip() for l in f.readlines()]

additional_excludes = ["t", "kb", "http", "pm", "ppt", "trac", "https", "mb"]

def valid(tok: str) -> bool:
    if tok in stop_words:
        return False
    if tok.isdigit():
        return False
    if tok in additional_excludes:
        return False
    return True

with open("bank.json", "r") as f:
    data = json.loads(f.read())

tokens = [tok for tok in sorted(data[1].items(), key = lambda x: (-x[1], x[0])) if valid(tok[0])]

with open("top50.txt", "w") as f:
    f.write("\n".join(f"{tok}: {val}" for tok,val in tokens[:50]))