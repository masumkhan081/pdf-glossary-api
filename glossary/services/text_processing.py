import re
from collections import Counter


def count_words(text):
    words = re.findall(r"\b[\w']+\b", text.casefold())
    return dict(Counter(words))
