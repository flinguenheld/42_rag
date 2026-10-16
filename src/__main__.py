import fire

from src.commands import (
    answer,
    answer_dataset,
    evaluate,
    index,
    search,
    search_dataset,
)


# ############################################################################
# ################################################################### MAIN ###
def main() -> None:
    print("Hello from rag!")


if __name__ == "__main__":
    main()
    fire.Fire(
        {
            "index": index,
            "search": search,
            "answer": answer,
            "search_dataset": search_dataset,
            "answer_dataset": answer_dataset,
            "evaluate": evaluate,
        }
    )
