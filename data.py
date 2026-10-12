import os

FOLDER_PROCESSED = "./data/processed/"
FOLDER_BM25 = "bm25"
FILE_CHUNKS = "chunks.json"
FOLDER_RAW = "./vllm-0.10.1"


def set_exports():
    os.environ["UV_PROJECT_ENVIRONMENT"] = "~/goinfre/rag_cache/.venv/"
    os.environ["HF_HUB_CACHE"] = "~/goinfre/rag_cache/hugging_face/"
    os.environ["HF_HOME"] = "~/goinfre/rag_cache/hugging_face/"
    os.environ["UV_CACHE_DIR"] = "~/goinfre/rag_cache/uv/"
