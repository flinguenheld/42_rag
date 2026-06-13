from src.llm.llm_wrapper import LLMWrapper


def main() -> None:
    print("Hello from rag!")

    llm = LLMWrapper()

    print(llm.ask("Hello", 50))


if __name__ == "__main__":
    main()
