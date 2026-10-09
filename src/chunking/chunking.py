from collections.abc import Callable
from pathlib import Path

from rank_bm25 import BM25Okapi
from tqdm import tqdm

from src.chunking.markdown import chunk_markdown, tokenize_markdown
from src.chunking.python import chunk_code, tokenize_python


class FileManagerException(Exception):
    pass


class FileManager:
    FOLDER = "./vllm-0.10.1"

    def run(self):

        path = Path(FileManager.FOLDER)
        if not path.exists():
            raise FileManagerException(
                f"The folder {FileManager.FOLDER} does not exist"
            )
        else:
            python_files = list(path.rglob("*.py"))
            markdown_files = list(path.rglob("*.md"))

            if not python_files and not markdown_files:
                raise FileManagerException("There's no file to chunck")

            # print(f"I'm running {len(python_files)} python files")
            # print(f"I'm running {len(markdown_files)} markdown files")
            # for f in python_files:
            #     print(f" - {f}")

            records: list[tuple[str, str]] = []  # (file_path, chunk)

            print("# ############## Chunking python files ##")
            with tqdm(total=len(python_files)) as t:
                for file in python_files:
                    source = file.read_text(encoding="utf-8")
                    for chunk in chunk_code(source):
                        records.append((str(path), chunk))

                    t.update()
            index = ChunkIndex(records, tokenize=tokenize_python)

            records_md: list[tuple[str, str]] = []  # (file_path, chunk)
            print("# ############## Chunking markdown files ##")
            with tqdm(total=len(markdown_files)) as t:
                for file in markdown_files:
                    source = file.read_text(encoding="utf-8")
                    for chunk in chunk_markdown(source):
                        records_md.append((str(path), chunk))
                    t.update()

            index_md = ChunkIndex(records_md, tokenize=tokenize_markdown)


# ############################################################################
# BM25 index
class ChunkIndex:
    def __init__(self, records: list[tuple[str, str]], tokenize: Callable):
        self.records = records
        self.tokenize = tokenize
        self.bm25 = (
            BM25Okapi([tokenize(c) for _, c in records]) if records else None
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[tuple[str, str, float]]:
        if not self.bm25:
            return []
        scores = self.bm25.get_scores(self.tokenize(query))
        ranked = sorted(zip(self.records, scores), key=lambda x: -x[1])
        return [
            (path, chunk, score)
            for (path, chunk), score in ranked[:top_k]
            if score > 0
        ]
