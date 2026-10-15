from typing import Any

from src.answering.answering import answer_question
from src.chunking.file_manager import FileManager
from src.indexing.indexer import Indexer
from src.indexing.searcher import Searcher
from src.llm.llm_wrapper import LLMWrapper
from src.models import MinimalSource, UnansweredQuestion


# ############################################################################
# ################################################################## INDEX ###
def index(max_chunk_size: int = 2000) -> None:

    if Helpers.is_chunk_size_valid(max_chunk_size):
        records = FileManager(max_chunk_size).run()
        indexer = Indexer(records)
        indexer.save()


# ############################################################################
# ################################################################# SEARCH ###
def search(question: str, k: int = 5) -> None:

    question = str(question).strip()
    if Helpers.is_question_valid(question, k):
        searcher = Searcher()
        records = searcher.search(question, k)

        print("Records:\n")
        Helpers.print_records(records)


# ############################################################################
# ################################################################# ANSWER ###
def answer(question: str, k: int = 5) -> None:

    question = str(question).strip()
    if Helpers.is_question_valid(question, k):
        searcher = Searcher()
        records = searcher.search(question, k)

        llm = LLMWrapper()
        answered = answer_question(
            llm, UnansweredQuestion(question=question), sources=records
        )

        print("Question:")
        print(f"{answered.question} [{answered.question_id}]\n")

        print("Sources:")
        Helpers.print_records(answered.retrieved_sources)

        print("\nAnswer:")
        print(answered.answer)


# ############################################################################
# ################################################################ HELPERS ###
class Helpers:
    @staticmethod
    def is_chunk_size_valid(max_chunk_size: Any) -> bool:

        if not isinstance(max_chunk_size, int):
            print("max_chunk_size has to be an integer.")
            return False

        if max_chunk_size <= 1:
            print("max_chunk_size cannot be lower than 2.")
            return False

        if max_chunk_size > 2000:
            print("max_chunk_size cannot be higher than 2000.")
            return False

        return True

    @staticmethod
    def is_question_valid(question: str, k: int) -> bool:

        if not isinstance(k, int) or k <= 0:
            print("k has to be an integer of at least 1.")
            return False

        if not question:
            print("The question cannot be empty.")
            return False

        return True

    @staticmethod
    def print_records(records: list[MinimalSource]) -> None:

        for i, rec in enumerate(records):
            print(
                f"{i + 1} -> file: {rec.file_path} "
                f"[{rec.first_character_index}:{rec.last_character_index}]"
            )
