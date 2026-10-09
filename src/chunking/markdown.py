import re

from chonkie import RecursiveChunker


# ############################################################################
# Markdown-aware tokenization for BM25
def tokenize_markdown(text: str) -> list[str]:
    """Lowercased word tokens; keeps words like "don't"
    and "state-of-the-art" intact.
    Markdown syntax (#, *, [, ], ...) is ignored: it's structure, not content.
    """
    token_regex = re.compile(r"[\w]+(?:['’-]\w+)?")
    return [w.lower() for w in token_regex.findall(text)]


# ############################################################################
# Chunking: structure-aware, keeps titles & paragraphs
def chunk_markdown(source: str, chunk_size: int = 2000) -> list[str]:
    """
    One chunk per section/paragraph block, with heading context prepended.
    """
    md_chunker = RecursiveChunker.from_recipe(
        "markdown", lang="en", chunk_size=chunk_size
    )

    return [chunk.text for chunk in md_chunker.chunk(source)]
