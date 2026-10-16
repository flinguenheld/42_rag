import fire

from data import set_exports
from src.commands import answer, index, search, search_dataset


# ############################################################################
# ################################################################### MAIN ###
def main() -> None:
    print("Hello from rag!")
    set_exports()


if __name__ == "__main__":
    main()
    fire.Fire(
        {
            "index": index,
            "search": search,
            "answer": answer,
            "search_dataset": search_dataset,
        }
    )
