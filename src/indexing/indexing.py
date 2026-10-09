from pathlib import Path

import bm25s

from src.chunking.markdown import tokenize_markdown
from src.chunking.python import tokenize_python


class Retriever:
    def __init__(self, records: list[tuple[str, str]]):
        self.records = records  # (file_path, chunk)
        corpus_tokens = [
            self._tokenize(file, chunk) for file, chunk in records
        ]
        self.bm25 = bm25s.BM25()
        self.bm25.index(corpus_tokens)

    def search(self, question: str, k: int = 10) -> list[tuple[str, str]]:
        query_tokens = tokenize_python(question)
        indices, _scores = self.bm25.retrieve(
            [query_tokens], k=min(k, len(self.records))
        )
        return [self.records[i] for i in indices[0]]

    def _tokenize(self, file: str, text: str) -> list[str]:
        """Pick the tokenizer according to the file type."""
        if Path(file).suffix == ".py":
            return tokenize_python(text)
        return tokenize_markdown(text)
