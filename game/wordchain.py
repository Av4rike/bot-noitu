import json
import random
import os
DATA_PATH = "data/memory.json"
markov = {}
def load_memory():
    global markov
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            markov = json.load(f)
    else:
        markov = {}
def save_memory():
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(markov, f, ensure_ascii=False, indent=2)
def learn(sentence: str):
    words = sentence.lower().split()
    for i in range(len(words) - 1):
        markov.setdefault(words[i], []).append(words[i + 1])
def generate(start_word: str, max_len=6):
    if start_word not in markov:
        return None
    result = [start_word]
    cur = start_word
    for _ in range(max_len - 1):
        if cur not in markov:
            break
        cur = random.choice(markov[cur])
        result.append(cur)
    return " ".join(result)
def last_word(text: str):
    return text.lower().split()[-1]