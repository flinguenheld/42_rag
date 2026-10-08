from src.chunking.markdown import chunk_markdown, MarkdownChunkIndex
from pathlib import Path

from tqdm import tqdm

from src.chunking.python import ChunkIndex, chunk_code


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
            index = ChunkIndex(records)

            records_md: list[tuple[str, str]] = []  # (file_path, chunk)
            print("# ############## Chunking markdown files ##")
            with tqdm(total=len(markdown_files)) as t:
                for file in markdown_files:
                    source = file.read_text(encoding="utf-8")
                    for chunk in chunk_markdown(source):
                        records_md.append((str(path), chunk))
                    t.update()

            index_md = MarkdownChunkIndex(records_md)


# Open folder

# Read all files

# Chunk with the lib

# Display a bar
