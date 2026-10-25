import pytest
from app.categories import BugCategory, CATEGORY_DEFINITIONS, get_category_metadata


def test_eight_canonical_categories():
    assert len(BugCategory) == 8
    assert len(CATEGORY_DEFINITIONS) == 8

    expected_categories = {
        "syntax_error",
        "undefined_name",
        "type_error",
        "index_out_of_range",
        "wrong_operator",
        "missing_return",
        "loop_boundary",
        "wrong_variable",
    }
    actual_categories = {cat.value for cat in BugCategory}
    assert actual_categories == expected_categories


def test_category_metadata():
    for cat in BugCategory:
        meta = get_category_metadata(cat)
        assert meta is not None
        assert meta.display_name != ""
        assert meta.concept != ""
        assert meta.description != ""
        assert meta.pedagogical_nudge_example != ""
