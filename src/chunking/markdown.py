import re
from rank_bm25 import BM25Okapi
from chonkie import RecursiveChunker


def chunk_markdown(
    content: str,
    chunk_size: int = 2048,
):
    """Chunk a single Markdown file using Chonkie's RecursiveChunker."""

    # Create the recursive chunker
    chunker = RecursiveChunker.from_recipe(
        "markdown",
        lang="en",
        chunk_size=chunk_size,
        min_characters_per_chunk=100,
    )

    return chunker.chunk(content)


def tokenize_markdown(text: str) -> list[str]:
    # Remove fenced code block markers, but keep the code/content.
    text = re.sub(r"```[\w+-]*", " ", text)
    text = text.replace("```", " ")

    # Markdown links: keep the visible text, drop the URL.
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

    # Images: keep alt text.
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)

    # Headings / blockquotes.
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*>\s?", "", text, flags=re.MULTILINE)

    # Lists.
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

    # Bold / italic / inline code.
    text = re.sub(r"[*_~`]", "", text)

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    # Tokenize.
    return re.findall(r"\b\w+\b", text.lower())


class MarkdownChunkIndex:
    def __init__(self, records: list[tuple[str, str]]):
        # records = list of (file_path, markdown_chunk)
        self.records = records

        self.bm25 = (
            BM25Okapi([tokenize_markdown(chunk) for _, chunk in records])
            if records
            else None
        )

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[tuple[str, str, float]]:
        if self.bm25 is None:
            return []

        scores = self.bm25.get_scores(tokenize_markdown(query))

        ranked = sorted(
            zip(self.records, scores),
            key=lambda x: -x[1],
        )

        return [
            (path, chunk, score)
            for (path, chunk), score in ranked[:top_k]
            if score > 0
        ]
