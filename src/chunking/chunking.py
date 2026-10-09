from pathlib import Path

from tqdm import tqdm

from src.chunking.markdown import chunk_markdown
from src.chunking.python import chunk_code


class FileManagerException(Exception):
    pass


class FileManager:
    FOLDER = "./vllm-0.10.1"

    def run(self) -> list[tuple[str, str]]:
        """Returns a list of (file_path, chunk)."""
        path = Path(self.FOLDER)
        if not path.exists():
            raise FileManagerException(
                f"The folder {self.FOLDER} does not exist"
            )

        # one dict: extension -> chunking function
        chunkers = {"*.py": chunk_code, "*.md": chunk_markdown}

        records: list[tuple[str, str]] = []
        for pattern, chunker in chunkers.items():
            files = list(path.rglob(pattern))
            for file in tqdm(files, desc=f"Chunking {pattern}"):
                source = file.read_text(encoding="utf-8", errors="ignore")
                for chunk in chunker(source):
                    records.append((str(file), chunk))

        if not records:
            raise FileManagerException("There's no file to chunk")
        return records
