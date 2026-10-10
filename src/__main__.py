import os

import fire

from src.chunking.chunking import FileManager
from src.indexing.indexing import Retriever


def main() -> None:

    print("Hello from rag!")
    set_exports()

    # index()
    # llm = LLMWrapper()

    # answer = llm.ask("Hello", 50)
    # print(f"Hello: '{answer}'")


class Index:
    def index(self, max_chunk_size: int = 2000) -> None:
        records = FileManager(max_chunk_size).run()
        retriever = Retriever(records)

        question = input("Question: ")
        for file, (chunk, start, end) in retriever.search(question):
            print(f"\n--- {file} --- {start}:{end}")


def set_exports():
    os.environ["UV_PROJECT_ENVIRONMENT"] = "~/goinfre/rag_cache/.venv/"
    os.environ["HF_HUB_CACHE"] = "~/goinfre/rag_cache/hugging_face/"
    os.environ["HF_HOME"] = "~/goinfre/rag_cache/hugging_face/"
    os.environ["UV_CACHE_DIR"] = "~/goinfre/rag_cache/uv/"


if __name__ == "__main__":
    main()
    fire.Fire(Index)
