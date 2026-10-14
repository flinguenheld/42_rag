import re

# A "word" is a run of letters, digits and underscores (an identifier).
WORD_REGEX = re.compile(r"[A-Za-z0-9_]+")

# Parts of an identifier: acronyms (HTTP), capitalized or lowercase
# words (Server, max) and numbers (3).
PART_REGEX = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+")


def tokenize(text: str) -> list[str]:
    """Split a text into lowercase tokens for BM25.

    Used for code, Markdown and questions alike. Each word is kept whole,
    then its snake_case / camelCase parts are added, so that both
    "max_chunk_size" and "max chunk size" can match. Punctuation is dropped.

    Args:
        text: The text to tokenize.

    Returns:
        The list of tokens, e.g. "HTTPServer.max_size" gives
        ["httpserver", "http", "server", "max_size", "max", "size"].
    """
    tokens: list[str] = []
    for word in WORD_REGEX.findall(text):
        whole = word.lower()
        tokens.append(whole)
        for part in PART_REGEX.findall(word):
            if part.lower() != whole:
                tokens.append(part.lower())
    return tokens
