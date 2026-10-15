import fire

from data import set_exports
from src.commands import answer, index, search


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
        }
    )
