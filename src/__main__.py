from src.chunking.chunking import FileManager
from src.indexing.indexing import Retriever


def main() -> None:
    print("Hello from rag!")

    # llm = LLMWrapper()

    # answer = llm.ask("Hello", 50)
    # print(f"Hello: '{answer}'")

    records = FileManager().run()
    retriever = Retriever(records)

    question = input("Question: ")
    for file, chunk in retriever.search(question):
        print(f"\n--- {file} ---\n{chunk[:300]}")


if __name__ == "__main__":
    main()
