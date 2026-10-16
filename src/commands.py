import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError
from tqdm import tqdm

from data import FOLDER_PROCESSED
from src.answering.answering import answer_question
from src.chunking.file_manager import FileManager, FileManagerException
from src.indexing.indexer import Indexer
from src.indexing.searcher import Searcher
from src.llm.llm_wrapper import LLMWrapper
from src.models import (
    MinimalSearchResults,
    MinimalSource,
    RagDataset,
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
    UnansweredQuestion,
)


class CommandError(Exception):
    """An expected error, with a message for the user."""


# ############################################################################
# ################################################################## INDEX ###
def index(max_chunk_size: int = 2000) -> None:

    try:
        _Helper.check_chunk_size(max_chunk_size)
        records = FileManager(max_chunk_size).run()
        Indexer(records).save()
        print(f"Ingestion complete! Indices saved under {FOLDER_PROCESSED}")

    except FileManagerException as error:
        print(error)
    except OSError:
        print(f"The index cannot be written in '{FOLDER_PROCESSED}'.")
    except CommandError as error:
        print(error)


# ############################################################################
# ################################################################# SEARCH ###
def search(question: str, k: int = 5) -> None:

    try:
        question = str(question).strip()
        _Helper.check_question(question)
        _Helper.check_k(k)
        searcher = _Helper.load_searcher()
        records = searcher.search(question, k)

        print("Records:\n")
        _Helper.print_records(records)

    except CommandError as error:
        print(error)


# ############################################################################
# ################################################################# ANSWER ###
def answer(question: str, k: int = 5) -> None:

    try:
        question = str(question).strip()
        _Helper.check_question(question)
        _Helper.check_k(k)
        searcher = _Helper.load_searcher()
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

    except CommandError as error:
        print(error)


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
# ######################################################### ANSWER DATASET ###
def answer_dataset(
    student_search_results_path: str,
    save_directory: str,
) -> None:

    def prepare_save_path(file_name: str) -> Path:
        """Create the save folder before the slow LLM loop, fail fast."""

        folder = Path(save_directory)
        try:
            folder.mkdir(parents=True, exist_ok=True)
        except OSError:
            raise CommandError(f"The folder '{folder}' cannot be created.")

        if not os.access(folder, os.W_OK):
            raise CommandError(f"The folder '{folder}' is not writable.")

        return folder / file_name

    # #######################################
    # #######################################
    path_results = Path(student_search_results_path)
    try:
        results = _Helper.load_json(path_results, StudentSearchResults)
        path_save = prepare_save_path(path_results.name)

        answers = []
        llm = LLMWrapper()
        for res in tqdm(results.search_results):
            answers.append(
                answer_question(
                    llm,
                    unanswered=UnansweredQuestion(
                        question_id=res.question_id,
                        question=res.question,
                    ),
                    sources=res.retrieved_sources,
                )
            )
        results_and_answers = StudentSearchResultsAndAnswer(
            search_results=answers,
            k=results.k,
        )

        _Helper.save_json(results_and_answers, path_save)
        print(f"Questions with sources and answer saved in '{path_save}'.")

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
    def check_chunk_size(max_chunk_size: Any) -> None:

        if not isinstance(max_chunk_size, int):
            raise CommandError("max_chunk_size has to be an integer.")

        if max_chunk_size <= 1:
            raise CommandError("max_chunk_size cannot be lower than 2.")

        if max_chunk_size > 2000:
            raise CommandError("max_chunk_size cannot be higher than 2000.")

    @staticmethod
    def check_question(question: str) -> None:

        if not question:
            raise CommandError("The question cannot be empty.")

    @staticmethod
    def print_records(records: list[MinimalSource]) -> None:

        if not records:
            print("No relevant source found.")

        for i, rec in enumerate(records):
            print(
                f"{i + 1} -> file: {rec.file_path} "
                f"[{rec.first_character_index}:{rec.last_character_index}]"
            )
