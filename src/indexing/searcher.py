import json
from pathlib import Path

import bm25s

from data import FILE_CHUNKS, FOLDER_BM25, FOLDER_PROCESSED
from src.indexing.tokenizer import tokenize
from src.models import MinimalSource


class Searcher:
    def __init__(self) -> None:
        path = Path(FOLDER_PROCESSED)
        self.bm25 = bm25s.BM25.load(
            path / FOLDER_BM25,
            mmap=True,
            show_progress=True,
        )
        raw = (path / FILE_CHUNKS).read_text()
        self.records = [MinimalSource(**record) for record in json.loads(raw)]

    def is_empty(self) -> bool:
        return not self.records

    def search(self, question: str, k: int = 10) -> list[MinimalSource]:
        """
        Get the k first answers for python & markdown.
        A score of 0 means no word in common with the question
        (empty, punctuation only or unknown words): such chunks are dropped.
        """
        k = min(k, len(self.records))

        documents, scores = self.bm25.retrieve(
            [tokenize(question)],
            k=k,
            show_progress=False,
        )
        return [
            self.records[idx]
            for idx, score in zip(documents[0], scores[0])
            if score > 0
        ]
