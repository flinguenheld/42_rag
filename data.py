import os

FOLDER_PROCESSED = "./data/processed/"
FOLDER_BM25 = "bm25"
FILE_CHUNKS = "chunks.json"
FOLDER_RAW = "./data/raw/"


def set_exports() -> None:
    os.environ["HF_HUB_CACHE"] = os.path.expanduser(
        "~/goinfre/rag_cache/hugging_face"
    )
    os.environ["HF_HOME"] = os.path.expanduser(
        "~/goinfre/rag_cache/hugging_face"
    )
