import json
from pathlib import Path

import bm25s

from data import FILE_CHUNKS, FOLDER_BM25, FOLDER_PROCESSED
from src.chunking.markdown import tokenize_markdown
from src.chunking.python import tokenize_python


class Indexer:
    def __init__(self, records: list[tuple[str, tuple[str, int, int]]]):
        self.records = records  # (file_path, (text, start, end))

    def save(self) -> None:
        folder = Path(FOLDER_PROCESSED)
        folder.mkdir(parents=True, exist_ok=True)

        bm25 = bm25s.BM25()
        bm25.index(
            [
                self._get_tokenizer(file, chunk[0])
                for file, chunk in self.records
            ]
        )
        bm25.save(folder / FOLDER_BM25)
        (folder / FILE_CHUNKS).write_text(json.dumps(self.records))

    def _get_tokenizer(self, file: str, text: str) -> list[str]:
        tokenizer = (
            tokenize_python
            if Path(file).suffix == ".py"
            else tokenize_markdown
        )
        return tokenizer(text)
