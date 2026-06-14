from src.llm.llm_wrapper import LLMWrapper


def main() -> None:
    print("Hello from rag!")

    llm = LLMWrapper()

    answer = llm.ask("Hello", 50)
    print(f"Hello: '{answer}'")


if __name__ == "__main__":
    main()
