from chonkie import CodeChunker

from src.models import MinimalSource


# ############################################################################
# Chunking: chonkie CodeChunker (tree-sitter AST boundaries)
class ChunkerPython:
    def __init__(self, chunk_size: int = 2000) -> None:
        self.chunker = CodeChunker(
            language="python",
            tokenizer="character",  # only used to measure chunk size
            chunk_size=chunk_size,  # max tokens per chunk
        )

    def chunk(self, source: str, file_path: str) -> list[MinimalSource]:
        """Structure-aware chunking: never splits mid-function/mid-class."""

        # Chunker works with bytes, it allows to convert start/end in char pos
        source_bytes = source.encode("utf-8")

        return [
            MinimalSource(
                file_path=file_path,
                first_character_index=len(
                    source_bytes[: c.start_index].decode("utf-8")
                ),
                last_character_index=len(
                    source_bytes[: c.end_index].decode("utf-8")
                ),
            )
            for c in self.chunker.chunk(source)
        ]
