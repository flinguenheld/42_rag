import json
from pathlib import Path

import bm25s

from data import FILE_CHUNKS, FOLDER_BM25, FOLDER_PROCESSED
from src.indexing.tokenizer import tokenize
from src.models import MinimalSource


class Searcher:
    def __init__(self) -> None:
        path = Path(FOLDER_PROCESSED)
        self.bm25 = bm25s.BM25.load(path / FOLDER_BM25, mmap=True)
        raw = (path / FILE_CHUNKS).read_text()
        self.records = [MinimalSource(**record) for record in json.loads(raw)]

    def search(self, question: str, k: int = 10) -> list[MinimalSource]:
        """
        Get the k first answers for python & markdown.
        """
        k = min(k, len(self.records))
        return [
            self.records[idx]
            for idx, _scores in self.bm25.retrieve([tokenize(question)], k=k)
        ]
