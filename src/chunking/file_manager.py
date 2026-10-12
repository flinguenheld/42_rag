from pathlib import Path

from tqdm import tqdm

import data
from src.chunking.markdown import chunk_markdown
from src.chunking.python import chunk_code
from src.models import MinimalSource

# RENAME FILE ##############################################################
# RENAME FILE ##############################################################
# RENAME FILE ##############################################################


class FileManagerException(Exception):
    pass


class FileManager:
    FOLDER = "./vllm-0.10.1"

    def __init__(self, max_chunk_size: int):
        self.max_chunk_size = max_chunk_size

    def run(self) -> list[MinimalSource]:
        """Returns a list of (file_path, chunk)."""
        path = Path(data.FOLDER_RAW)
        if not path.exists():
            raise FileManagerException(
                f"The folder {data.FOLDER_RAW} does not exist"
            )

        # one dict: extension -> chunking function
        chunkers = {"*.py": chunk_code, "*.md": chunk_markdown}

        records: list[MinimalSource] = []
        for pattern, chunker in chunkers.items():
            files = list(path.rglob(pattern))
            for file in tqdm(files, desc=f"Chunking {pattern}"):
                records.extend(
                    chunker(
                        source=file.read_text(
                            encoding="utf-8", errors="ignore"
                        ),
                        file_path=str(file),
                        chunk_size=self.max_chunk_size,
                    )
                )

        if not records:
            raise FileManagerException("There's no file to chunk")
        return records
