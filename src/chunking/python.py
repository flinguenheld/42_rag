import re

from chonkie import CodeChunker
from rank_bm25 import BM25Okapi

TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+|[^\s\w]")


# ############################################################################
# Code-aware tokenization for BM25
def tokenize(text: str) -> list[str]:
    """Split identifiers, numbers and punctuation; lowercase everything.

    Also expands camelCase/PascalCase: "validateUserInput"
    -> validate, validateuserinput, user, input (lowercased).
    """
    words = TOKEN_RE.findall(text)
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
    chunk_size: int = 2048,
) -> list[str]:
    """Structure-aware chunking: never splits mid-function/mid-class."""
    chunker = CodeChunker(
        language=language,
        tokenizer="character",  # only used to measure chunk size
        chunk_size=chunk_size,  # max tokens per chunk
    )
    return [chunk.text for chunk in chunker.chunk(source)]


# ############################################################################
# BM25 index
class ChunkIndex:
    def __init__(self, records: list[tuple[str, str]]):
        # records = list of (file_path, chunk_text)
        self.records = records
        self.bm25 = (
            BM25Okapi([tokenize(c) for _, c in records]) if records else None
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[tuple[str, str, float]]:
        if not self.bm25:
            return []
        scores = self.bm25.get_scores(tokenize(query))
        ranked = sorted(zip(self.records, scores), key=lambda x: -x[1])
        return [
            (path, chunk, score)
            for (path, chunk), score in ranked[:top_k]
            if score > 0
        ]
