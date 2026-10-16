from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError
from tqdm import tqdm

from src.answering.answering import answer_question
from src.chunking.file_manager import FileManager
from src.indexing.indexer import Indexer
from src.indexing.searcher import Searcher
from src.llm.llm_wrapper import LLMWrapper
from src.models import (
    MinimalSearchResults,
    MinimalSource,
    RagDataset,
    StudentSearchResults,
    UnansweredQuestion,
)


class CommandError(Exception):
    """An expected error, with a message for the user."""


# ############################################################################
# ################################################################## INDEX ###
def index(max_chunk_size: int = 2000) -> None:

    if _Helper.is_chunk_size_valid(max_chunk_size):
        records = FileManager(max_chunk_size).run()
        indexer = Indexer(records)
        indexer.save()


# ############################################################################
# ################################################################# SEARCH ###
def search(question: str, k: int = 5) -> None:

    question = str(question).strip()
    if _Helper.is_question_valid(question, k):
        searcher = Searcher()
        records = searcher.search(question, k)

        print("Records:\n")
        _Helper.print_records(records)


# ############################################################################
# ################################################################# ANSWER ###
def answer(question: str, k: int = 5) -> None:

    question = str(question).strip()
    if _Helper.is_question_valid(question, k):
        searcher = Searcher()
        records = searcher.search(question, k)

        unanswered = UnansweredQuestion(question=question)

        print("Question:")
        print(f"{unanswered.question} [{unanswered.question_id}]\n")

        llm = LLMWrapper()
        answered = answer_question(llm, unanswered, sources=records)

        print("Sources:")
        _Helper.print_records(answered.retrieved_sources)

        print("\nAnswer:")
        print(answered.answer)


# ############################################################################
# ######################################################### SEARCH DATASET ###
def search_dataset(dataset_path: str, save_directory: str, k: int = 5) -> None:
    """
    Open the dataset file to get all questions.
    Perform a research for all of them.
    Save a json file with all questions and their sources.
    """

    def build_results(
        searcher: Searcher,
        dataset: list[UnansweredQuestion],
    ) -> list[MinimalSearchResults]:

        minimal_search_results = []
        for question in tqdm(dataset):
            minimal_search_results.append(
                MinimalSearchResults(
                    question_id=question.question_id,
                    question=question.question,
                    retrieved_sources=searcher.search(question.question, k),
                )
            )
        return minimal_search_results

    # #######################################
    # #######################################
    try:
        _Helper.check_k(k)
        searcher = _Helper.load_searcher()
        path_dataset = Path(dataset_path)
        dataset = _Helper.load_json(path_dataset, RagDataset)

        results = StudentSearchResults(
            search_results=build_results(searcher, dataset.rag_questions),
            k=k,
        )

        path_save = Path(save_directory) / path_dataset.name
        _Helper.save_json(results, path_save)
        print(f"Questions with their sources saved in '{path_save}'.")

    except CommandError as error:
        print(error)


# ############################################################################
# ################################################################ HELPERS ###
class _Helper:
    @staticmethod
    def check_k(k: Any) -> None:

        if not isinstance(k, int) or k <= 0:
            raise CommandError("k has to be an integer of at least 1.")

    @staticmethod
    def load_searcher() -> Searcher:

        try:
            searcher = Searcher()
        except FileNotFoundError:
            raise CommandError("No index found. Run 'index' first.")
        except ValueError:
            raise CommandError("The index is corrupted. Run 'index' again.")

        if searcher.is_empty():
            raise CommandError("The index is empty. Run 'index' first.")

        return searcher

    @staticmethod
    def load_json[T: BaseModel](path: Path, model: type[T]) -> T:

        try:
            return model.model_validate_json(path.read_text())
        except FileNotFoundError:
            raise CommandError(f"The file '{path}' does not exist.")
        except ValidationError:
            raise CommandError(
                f"The file '{path}' is not a valid {model.__name__}."
            )
        except (OSError, UnicodeDecodeError):
            raise CommandError(f"The file '{path}' cannot be read.")

    @staticmethod
    def save_json(model: BaseModel, path: Path) -> None:

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(model.model_dump_json(indent=2))
        except OSError:
            raise CommandError(f"The file '{path}' cannot be written.")

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
