from src.models import MinimalSource


def build_prompt(
    question: str,
    sources: list[MinimalSource],
) -> str:
    context_parts: list[str] = []
    for i, src in enumerate(sources):
        text = src.read_text().strip()
        context_parts.append(f"[Source {i + 1}: {src.file_path}]\n{text}")
    context = "\n\n".join(context_parts) or "No relevant source found."

    return (
        "You are a documentation assistant for the vLLM codebase.\n"
        "Answer the question using ONLY the sources below.\n"
        "If the sources do not contain the answer, say so.\n"
        "Cite sources as [Source N]. Be concise.\n\n"
        f"### Sources\n{context}\n\n"
        f"### Question\n{question}"
    )


