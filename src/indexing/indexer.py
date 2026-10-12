import json
import shutil
from pathlib import Path

import bm25s

from data import FILE_CHUNKS, FOLDER_BM25, FOLDER_PROCESSED
from src.chunking.markdown import tokenize_markdown
from src.chunking.python import tokenize_python
from src.models import MinimalSource


class Indexer:
    def __init__(self, records: list[MinimalSource]):
        self.records = records

    def save(self) -> None:
        folder = self._create_folder()

        bm25 = bm25s.BM25()
        bm25.index(
            [
                self._tokenize(record.file_path, record.read_text())
                for record in self.records
            ]
        )
        bm25.save(folder / FOLDER_BM25)
        (folder / FILE_CHUNKS).write_text(
            json.dumps([record.model_dump() for record in self.records])
        )

    def _tokenize(self, file: str, text: str) -> list[str]:
        if Path(file).suffix == ".py":
            return tokenize_python(text)
        else:
            return tokenize_markdown(text)

    def _create_folder(self) -> Path:
        folder = Path(FOLDER_PROCESSED)
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True, exist_ok=True)

        return folder
