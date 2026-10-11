import fire

from data import set_exports
from src.chunking.chunking import FileManager
from src.indexing.indexer import Indexer
from src.indexing.searcher import Searcher


# ############################################################################
# ################################################################### MAIN ###
def main() -> None:
    print("Hello from rag!")
    set_exports()


# ############################################################################
# ################################################################## INDEX ###
def index(max_chunk_size: int = 2000) -> None:
    records = FileManager(max_chunk_size).run()
    indexer = Indexer(records)
    indexer.save()


# ############################################################################
# ################################################################# SEARCH ###
def search(question: str, k: int = 5) -> None:
    searcher = Searcher()
    answer = searcher.search(question, k)

    print("Answer:")
    for i, a in enumerate(answer):
        print(f"{i + 1} -> file: {a[0]} -> {a[1][1]}/{a[1][2]}")


if __name__ == "__main__":
    main()
    fire.Fire({"index": index, "search": search})
