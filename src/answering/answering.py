import os
from pathlib import Path

from tqdm import tqdm

from data import SOURCE_MAX_TOKENS
from src.llm.llm_wrapper import LLMWrapper
from src.models import MinimalAnswer, MinimalSource, UnansweredQuestion


# ############################################################################
# ########################################################### ANSWER QUEST ###
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
        checked_sources = []

    else:
        readable_sources = _Helper.keep_readable_sources(sources)
        checked_sources = _Helper.limit_amount_of_sources(
            llm, readable_sources
        )

        if not checked_sources:
            answer = "No relevant source found to answer this question."

        else:
            prompt = _Helper.build_prompt(unanswered.question, checked_sources)
            answer = llm.ask(prompt, max_new_tokens=max_new_tokens)

    return MinimalAnswer(
        question_id=unanswered.question_id,
        question=unanswered.question,
        retrieved_sources=checked_sources,
        answer=answer,
    )


# ############################################################################
# ################################################################ HELPERS ###
class _Helper:
    @staticmethod
    def keep_readable_sources(
        sources: list[MinimalSource],
    ) -> list[MinimalSource]:
        """
        Skip the sources whose file is missing or cannot be read,
        so the answer is built from the remaining ones.
        """

        readable = []
        for source in sources:
            path = Path(source.file_path)
            if path.is_file() and os.access(path, os.R_OK):
                readable.append(source)
            else:
                tqdm.write(f"Source skipped, cannot read '{path}'")

        return readable

    @staticmethod
    def build_prompt(
        question: str,
        sources: list[MinimalSource],
    ) -> str:
        context_parts: list[str] = []
        for i, source in enumerate(sources):
            context_parts.append(_Helper.format_source(i + 1, source))
        context = "\n\n".join(context_parts)

        return (
            f"Sources:\n{context}\n\n"
            f"Question: {question}\n\n"
            "Answer in a few sentences, using only the sources above. "
            "If they do not contain the answer, say you do not know."
        )

    @staticmethod
    def format_source(index: int, src: MinimalSource) -> str:
        return f"[Source {index}: {src.file_path}]\n{src.read_text().strip()}"

    @staticmethod
    def limit_amount_of_sources(
        llm: LLMWrapper,
        sources: list[MinimalSource],
    ) -> list[MinimalSource]:
        """
        Loop in the sources and accumulate them one by one as long as the limit
        of tokens has not been reached.
        Avoid them after the limit.
        """

        token_left = SOURCE_MAX_TOKENS
        source_kept = []

        for i, source in enumerate(sources):
            token_requiered = llm.count_tokens(
                _Helper.format_source(i + 1, source)
            )

            if token_left - token_requiered >= 0:
                token_left -= token_requiered
                source_kept.append(source)
            else:
                tqdm.write(
                    f"Only take the first {len(source_kept)} on {len(sources)}"
                )
                break

        return source_kept
