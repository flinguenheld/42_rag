import json
from pathlib import Path

import bm25s

from data import FILE_CHUNKS, FOLDER_BM25, FOLDER_PROCESSED
from src.chunking.python import tokenize_python


class Searcher:
    def __init__(self):
        path = Path(FOLDER_PROCESSED)
        self.bm25 = bm25s.BM25.load(path / FOLDER_BM25, mmap=True)
        self.records = json.loads((path / FILE_CHUNKS).read_text())

    def search(
        self,
        question: str,
        k: int = 10,
    ) -> list[tuple[str, tuple[str, int, int]]]:
        """
        Return found chuncks in the format:
        (file_path, (text, start, end))
        """

        indices, _scores = self.bm25.retrieve(
            [tokenize_python(question)], k=min(k, len(self.records))
        )
        return [self.records[i] for i in indices[0]]
