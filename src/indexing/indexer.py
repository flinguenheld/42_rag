import json
import shutil
from pathlib import Path

import bm25s

from data import FILE_CHUNKS, FOLDER_BM25, FOLDER_PROCESSED
from src.indexing.tokenizer import tokenize
from src.models import MinimalSource


class Indexer:
    def __init__(self, records: list[MinimalSource]) -> None:
        self.records = records
        self.bm25 = bm25s.BM25()

    def save(self) -> None:
        folder = self._create_folder()

        self.bm25.index(
            [tokenize(record.read_text()) for record in self.records]
        )
        self.bm25.save(folder / FOLDER_BM25)
        (folder / FILE_CHUNKS).write_text(
            json.dumps([record.model_dump() for record in self.records])
        )

    def _create_folder(self) -> Path:
        folder = Path(FOLDER_PROCESSED)
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True, exist_ok=True)

        return folder
