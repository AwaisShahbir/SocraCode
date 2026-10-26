from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.categories import BugCategory
from app.retrieval.examples_library import WORKED_EXAMPLES, WorkedExample, get_examples_by_category


class TFIDFExampleRetriever:
    """Retrieves relevant parallel worked examples for Level 4 hints using TF-IDF."""

    def __init__(self):
        self.examples = WORKED_EXAMPLES
        self.corpus = [
            f"{ex.title} {ex.problem_description} {ex.code} {ex.explanation}"
            for ex in self.examples
        ]
        self.vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b|[^\w\s]")
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)

    def retrieve(
        self,
        category: BugCategory,
        student_code: str,
        error_text: str = "",
        language: str = "python",
    ) -> WorkedExample:
        """Find the most similar worked example matching the bug category and language."""
        category_examples = get_examples_by_category(category, language=language)
        if not category_examples:
            # Fallback to first available example if category not found
            return self.examples[0]

        if len(category_examples) == 1:
            return category_examples[0]

        # If multiple examples exist for the category, use TF-IDF cosine similarity
        query_text = f"{student_code} {error_text}"
        query_vec = self.vectorizer.transform([query_text])

        best_score = -1.0
        best_example = category_examples[0]

        for ex in category_examples:
            idx = self.examples.index(ex)
            sim = cosine_similarity(query_vec, self.tfidf_matrix[idx : idx + 1])[0][0]
            if sim > best_score:
                best_score = sim
                best_example = ex

        return best_example


_default_retriever = TFIDFExampleRetriever()

def retrieve_worked_example(
    category: BugCategory,
    student_code: str,
    error_text: str = "",
    language: str = "python",
) -> WorkedExample:
    return _default_retriever.retrieve(category, student_code, error_text, language=language)
