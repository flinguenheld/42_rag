from src.llm.llm_wrapper import LLMWrapper
from src.chunking.chunking import FileManager


def main() -> None:
    print("Hello from rag!")

    # llm = LLMWrapper()

    # answer = llm.ask("Hello", 50)
    # print(f"Hello: '{answer}'")

    file_manager = FileManager()
    file_manager.run()


if __name__ == "__main__":
    main()
