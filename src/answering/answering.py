from src.llm.llm_wrapper import LLMWrapper
from src.models import MinimalAnswer, MinimalSource, UnansweredQuestion


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


def answer_question(
    llm: LLMWrapper,
    unanswered: UnansweredQuestion,
    sources: list[MinimalSource],
    max_new_tokens: int = 512,
) -> MinimalAnswer:
    """Generate the answer of one question from its retrieved sources.

    The model only writes the answer text, every other field is known
    by our code. Without question or sources, the model is not called.
    """
    if not unanswered.question.strip():
        answer = "No question was asked."
    elif not sources:
        answer = "No relevant source found to answer this question."
    else:
        prompt = build_prompt(unanswered.question, sources)
        answer = llm.ask(prompt, max_new_tokens=max_new_tokens)

    return MinimalAnswer(
        question_id=unanswered.question_id,
        question=unanswered.question,
        retrieved_sources=sources,
        answer=answer,
    )
