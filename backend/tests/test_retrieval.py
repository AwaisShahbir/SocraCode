import pytest
from app.categories import BugCategory
from app.retrieval.tfidf_matcher import retrieve_worked_example
from app.retrieval.examples_library import WORKED_EXAMPLES


def test_worked_examples_catalog():
    assert len(WORKED_EXAMPLES) >= 8
    categories = {ex.category for ex in WORKED_EXAMPLES}
    for cat in BugCategory:
        assert cat in categories, f"Missing worked example for category {cat}"


def test_tfidf_retrieval():
    code = "def get_item(arr):\n    return arr[len(arr)]"
    example = retrieve_worked_example(BugCategory.INDEX_OUT_OF_RANGE, code, "IndexError")
    assert example.category == BugCategory.INDEX_OUT_OF_RANGE
    assert "len" in example.code
    assert example.explanation != ""
