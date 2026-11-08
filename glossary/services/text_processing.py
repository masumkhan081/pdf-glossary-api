"""
Text processing service for English tokenisation and word frequency counting.

NOTE: This is a basic English tokenizer, not yet a glossary-term selector
or a multilingual tokenizer. It extracts ASCII alphabetic words, allows internal
apostrophes for contractions, excludes digit- and underscore-containing tokens,
and treats hyphens and em dashes as word separators.
"""

import re
from collections import Counter
from typing import Any

# Allowed ASCII alphabetic word with internal apostrophes (e.g. "freedom", "isn't", "o'clock")
WORD_PATTERN = re.compile(r"^[a-z]+(?:'[a-z]+)*$")

# Curly apostrophe normalisation mapping
CURLY_APOSTROPHES = str.maketrans({
    "\u2018": "'",  # Left single quotation mark
    "\u2019": "'",  # Right single quotation mark
    "\u201a": "'",  # Single low-9 quotation mark
    "\u201b": "'",  # Single high-reversed-9 quotation mark
})

# Hyphens and dashes to be treated as word separators
DASH_PATTERN = re.compile(r"[\u2013\u2014\u2015\-]")

# Candidate token pattern: sequences of lowercase letters, digits, underscores, and apostrophes
TOKEN_PATTERN = re.compile(r"[a-z0-9_']+")

# Pattern to detect excluded tokens (containing any digits or underscores)
EXCLUDED_PATTERN = re.compile(r"[\d_]")


def tokenize(text: str) -> list[str]:
    """
    Extract a list of valid English words from the input text.

    Rules:
    - Normalises case to lowercase.
    - Normalises curly apostrophes to straight apostrophes.
    - Treats hyphens and em/en dashes as word separators.
    - Excludes entire digit-containing or underscore-containing tokens.
    - Strips leading and trailing apostrophes from words.
    - Retains only ASCII alphabetic words with optional internal apostrophes.
    """
    if not text:
        return []

    # 1. Normalise case
    normalized = text.casefold()

    # 2. Normalise curly apostrophes to straight apostrophe
    normalized = normalized.translate(CURLY_APOSTROPHES)

    # 3. Treat hyphens and em/en dashes as word separators
    normalized = DASH_PATTERN.sub(" ", normalized)

    # 4. Extract candidate tokens (letters, digits, underscores, apostrophes)
    candidate_tokens = TOKEN_PATTERN.findall(normalized)

    words: list[str] = []
    for token in candidate_tokens:
        # Exclude entire digit-containing or underscore-containing tokens
        if EXCLUDED_PATTERN.search(token):
            continue

        # Strip surrounding apostrophes (e.g. 'quoted' -> quoted)
        cleaned = token.strip("'")

        # Validate: ASCII alphabetic word, allowing internal apostrophes
        if WORD_PATTERN.fullmatch(cleaned):
            words.append(cleaned)

    return words


def count_words(text: str) -> dict[str, int]:
    """
    Count word frequencies in the given text.
    Returns a dict mapping lowercase words to their integer frequency.
    """
    words = tokenize(text)
    return dict(Counter(words))


def analyse_text(text: str) -> dict[str, Any]:
    """
    Perform full text analysis on the given text.

    Returns a dict with:
    - total_words: sum of all word counts
    - unique_words: count of distinct words
    - words: list of dicts {"word": str, "count": int}, sorted by
             descending count, then alphabetically for ties.
    """
    counts = count_words(text)

    sorted_words = [
        {"word": word, "count": count}
        for word, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    return {
        "total_words": sum(counts.values()),
        "unique_words": len(counts),
        "words": sorted_words,
    }
