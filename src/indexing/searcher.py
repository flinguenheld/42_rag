import json
from pathlib import Path

import bm25s

from data import FILE_CHUNKS, FOLDER_BM25, FOLDER_PROCESSED
from src.chunking.markdown import tokenize_markdown
from src.chunking.python import tokenize_python
from src.models import MinimalSource


class Searcher:
    def __init__(self):
        path = Path(FOLDER_PROCESSED)
        self.bm25 = bm25s.BM25.load(path / FOLDER_BM25, mmap=True)
        raw = (path / FILE_CHUNKS).read_text()
        self.records = [MinimalSource(**record) for record in json.loads(raw)]

    def search(self, question: str, k: int = 10) -> list[MinimalSource]:
        """
        Get the k first answers for python & markdown.
        Mix and sort.
        Get the k first.
        """
        k = min(k, len(self.records))
        hits: list[tuple[float, int]] = []

        for tokenizer in (tokenize_python, tokenize_markdown):
            indices, scores = self.bm25.retrieve([tokenizer(question)], k=k)
            hits.extend(zip(scores[0], indices[0]))

        hits.sort(key=lambda hit: hit[0], reverse=False)
        return [self.records[i] for _score, i in hits[:k]]
