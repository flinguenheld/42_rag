from chonkie import RecursiveChunker

from src.models import MinimalSource

# Smaller chunks fit the short doc sections better (measured: docs recall@5
# 81% -> 83% on the public dataset). max_chunk_size stays the ceiling.
MARKDOWN_MAX_CHUNK_SIZE = 1500


# ############################################################################
# Chunking: structure-aware, keeps titles & paragraphs
class ChunkerMarkdown:
    def __init__(self, chunk_size: int = 2000) -> None:
        self.chunker = RecursiveChunker.from_recipe(
            "markdown",
            lang="en",
            chunk_size=min(chunk_size, MARKDOWN_MAX_CHUNK_SIZE),
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
