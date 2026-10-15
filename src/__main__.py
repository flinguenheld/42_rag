import fire

from data import set_exports
from src.answering.answering import answer_question
from src.chunking.file_manager import FileManager
from src.indexing.indexer import Indexer
from src.indexing.searcher import Searcher
from src.llm.llm_wrapper import LLMWrapper
from src.models import UnansweredQuestion


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
    records = searcher.search(question, k)

    print("Records:\n")
    for i, record in enumerate(records):
        print(
            f"{i + 1} -> file: {record.file_path} \
[{record.first_character_index}:{record.last_character_index}]"
        )


# ############################################################################
# ################################################################# ANSWER ###
def answer(question: str, k: int = 5) -> None:
    question = str(question).strip()

    if not isinstance(k, int) or k <= 0:
        print("k has to be an integer of at least 1.")
    elif not question:
        print("The question cannot be empty.")
    else:
        searcher = Searcher()
        records = searcher.search(question, k)

        llm = LLMWrapper()
        answered = answer_question(
            llm, UnansweredQuestion(question=question), sources=records
        )

        print("Question:")
        print(f"{answered.question} [{answered.question_id}]\n")

        print("Sources:")
        for i, rec in enumerate(answered.retrieved_sources):
            print(
                f"{i + 1} -> file: {rec.file_path} "
                f"[{rec.first_character_index}:{rec.last_character_index}]"
            )

        print("\nAnswer:")
        print(answered.answer)


if __name__ == "__main__":
    main()
    fire.Fire(
        {
            "index": index,
            "search": search,
            "answer": answer,
        }
    )
