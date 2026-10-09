import re

from chonkie import CodeChunker


# ############################################################################
# Code-aware tokenization for BM25
def tokenize_python(text: str) -> list[str]:
    """Split identifiers, numbers and punctuation; lowercase everything.

    Also expands camelCase/PascalCase: "validateUserInput"
    -> validate, validateuserinput, user, input (lowercased).
    """
    token_regex = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+|[^\s\w]")
    words = token_regex.findall(text)
    tokens: list[str] = []
    for w in words:
        tokens.append(w.lower())
        tokens.extend(p.lower() for p in re.findall(r"[A-Z][a-z0-9]*", w))
    return tokens


# ############################################################################
# Chunking: chonkie CodeChunker (tree-sitter AST boundaries)
def chunk_code(
    source: str,
    language: str = "python",
    chunk_size: int = 2000,
) -> list[str]:
    """Structure-aware chunking: never splits mid-function/mid-class."""
    chunker = CodeChunker(
        language=language,
        tokenizer="character",  # only used to measure chunk size
        chunk_size=chunk_size,  # max tokens per chunk
    )
    return [chunk.text for chunk in chunker.chunk(source)]
