from chonkie import RecursiveChunker

from src.models import MinimalSource


# ############################################################################
# Chunking: structure-aware, keeps titles & paragraphs
class ChunkerMarkdown:
    def __init__(self, chunk_size: int = 2000) -> None:
        self.chunker = RecursiveChunker.from_recipe(
            "markdown",
            lang="en",
            chunk_size=chunk_size,
        )

    def chunk(self, source: str, file_path: str) -> list[MinimalSource]:
        """
        One chunk per section/paragraph block.
        """

        return [
            MinimalSource(
                file_path=file_path,
                first_character_index=c.start_index,
                last_character_index=c.end_index,
            )
            for c in self.chunker.chunk(source)
        ]
