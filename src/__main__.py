import fire

from data import set_exports
from src.answering.answering import build_prompt
from src.chunking.file_manager import FileManager
from src.indexing.indexer import Indexer
from src.indexing.searcher import Searcher
from src.llm.llm_wrapper import LLMWrapper
from src.models import MinimalAnswer, MinimalSource


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
def search(question: str, k: int = 5) -> list[MinimalSource]:
    searcher = Searcher()
    records = searcher.search(question, k)

    print("Records:\n")
    for i, record in enumerate(records):
        print(f"{i + 1} -> file: {record}")

    return records


# ############################################################################
# ################################################################# ANSWER ###
# def answer(question: str, k: int = 5) -> MinimalAnswer:
def answer(question: str, k: int = 5) -> None:
    searcher = Searcher()
    records = searcher.search(question, k)

    llm = LLMWrapper()

    prompt = build_prompt(question, records)
    raw = llm.ask(prompt, max_new_tokens=2000)

    print("test generated:\n")
    print(raw)

    # return MinimalAnswer(
    #     question_id=...,
    #     question=question,
    #     retrieved_sources=sources,
    #     answer=raw,
    # )


if __name__ == "__main__":
    main()
    fire.Fire(
        {
            "index": index,
            "search": search,
            "answer": answer,
        }
    )
