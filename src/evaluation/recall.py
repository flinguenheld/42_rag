from src.models import (
    AnsweredQuestion,
    MinimalSource,
    RagDataset,
    StudentSearchResults,
)

IOU_THRESHOLD = 0.05  # intersection over union
K_VALUES = (1, 3, 5, 10)


# ############################################################################
# ##################################################### ANSWERED QUESTIONS ###
def answered_questions(dataset: RagDataset) -> list[AnsweredQuestion]:
    """Keep only the questions which have reference sources to compare to."""

    return [
        question
        for question in dataset.rag_questions
        if isinstance(question, AnsweredQuestion) and question.sources
    ]


# ############################################################################
# ############################################################# RECALL @ K ###
def recall_at_k(
    results: StudentSearchResults,
    questions: list[AnsweredQuestion],
) -> dict[int, float]:
    """Compute the recall@k for k in K_VALUES (up to the k of the results).

    For one question, recall@k is the share of its reference sources found
    in our top-k results. The dataset recall is the average over questions.
    A question missing from our results counts as 0.
    """

    retrieved = {
        result.question_id: result.retrieved_sources
        for result in results.search_results
    }
    k_values = sorted({k for k in K_VALUES if k <= results.k} | {results.k})

    recalls: dict[int, float] = {}
    for k in k_values:
        total = 0.0
        for question in questions:
            top_k = retrieved.get(question.question_id, [])[:k]
            found = sum(
                1
                for expected in question.sources
                if _Helper.is_found(expected, top_k)
            )
            total += found / len(question.sources)
        recalls[k] = total / len(questions)

    return recalls


# ############################################################################
# ################################################################ HELPERS ###
class _Helper:
    @staticmethod
    def iou(a: MinimalSource, b: MinimalSource) -> float:
        """Intersection over union of the character ranges of two sources."""

        start = max(a.first_character_index, b.first_character_index)
        end = min(a.last_character_index, b.last_character_index)
        intersection = max(0, end - start)

        union = max(a.last_character_index, b.last_character_index) - min(
            a.first_character_index, b.first_character_index
        )
        return intersection / union if union > 0 else 0.0

    @staticmethod
    def is_found(
        expected: MinimalSource,
        retrieved: list[MinimalSource],
    ) -> bool:
        """A source is found if one result is in the same file and overlaps it
        enough (the file path has to be exactly the same)."""

        return any(
            source.file_path == expected.file_path
            and _Helper.iou(source, expected) >= IOU_THRESHOLD
            for source in retrieved
        )
