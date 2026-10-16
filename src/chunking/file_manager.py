from pathlib import Path

from tqdm import tqdm

import data
from src.chunking.markdown import ChunkerMarkdown
from src.chunking.python import ChunkerPython
from src.models import MinimalSource


class FileManagerException(Exception):
    pass


class FileManager:
    def __init__(self, max_chunk_size: int) -> None:
        self.markdown_ck = ChunkerMarkdown(max_chunk_size)
        self.python_ck = ChunkerPython(max_chunk_size)

    def run(self) -> list[MinimalSource]:
        path = Path(data.FOLDER_RAW)
        if not path.exists():
            raise FileManagerException(
                f"The folder {data.FOLDER_RAW} does not exist"
            )

        # Manage python & markdown files separately
        records: list[MinimalSource] = []
        for pattern in ("*.py", "*.md", "*.txt"):
            files = list(path.rglob(pattern))
            for file in tqdm(files, desc=f"Chunking {pattern}"):
                source = file.read_text(encoding="utf-8", errors="ignore")
                file_path = str(file)

                if pattern == "*.py":
                    records.extend(self.python_ck.chunk(source, file_path))
                else:
                    records.extend(self.markdown_ck.chunk(source, file_path))

        if not records:
            raise FileManagerException("There's no file to chunk")
        return records
