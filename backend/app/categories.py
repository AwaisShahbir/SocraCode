"""
SocraCode Bug Category and Concept Taxonomy.
Defines the canonical 8 bug categories shared across the platform.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class BugCategory(str, Enum):
    """The canonical 8 bug categories defined in Section 4.2."""

    SYNTAX_ERROR = "syntax_error"
    UNDEFINED_NAME = "undefined_name"
    TYPE_ERROR = "type_error"
    INDEX_OUT_OF_RANGE = "index_out_of_range"
    WRONG_OPERATOR = "wrong_operator"
    MISSING_RETURN = "missing_return"
    LOOP_BOUNDARY = "loop_boundary"
    WRONG_VARIABLE = "wrong_variable"


class CategoryMetadata(BaseModel):
    category: BugCategory
    display_name: str
    concept: str
    description: str
    pedagogical_nudge_example: str


CATEGORY_DEFINITIONS: Dict[BugCategory, CategoryMetadata] = {
    BugCategory.SYNTAX_ERROR: CategoryMetadata(
        category=BugCategory.SYNTAX_ERROR,
        display_name="Syntax Error",
        concept="syntax_rules",
        description="Structural code errors like missing colons, unbalanced brackets, or invalid indentation.",
        pedagogical_nudge_example="Check the punctuation and structural symbols at the end of each header line.",
    ),
    BugCategory.UNDEFINED_NAME: CategoryMetadata(
        category=BugCategory.UNDEFINED_NAME,
        display_name="Undefined Name",
        concept="variable_scope_and_declaration",
        description="Attempting to use a variable or function that hasn't been declared or has a typo in its name.",
        pedagogical_nudge_example="Verify that every variable name you are reading has been spelled and assigned earlier.",
    ),
    BugCategory.TYPE_ERROR: CategoryMetadata(
        category=BugCategory.TYPE_ERROR,
        display_name="Type Incompatibility",
        concept="data_types",
        description="Applying operations between incompatible types (e.g. adding a string to an integer).",
        pedagogical_nudge_example="What type of data does each operand hold at this point in the calculation?",
    ),
    BugCategory.INDEX_OUT_OF_RANGE: CategoryMetadata(
        category=BugCategory.INDEX_OUT_OF_RANGE,
        display_name="Index Out of Range",
        concept="indexing_and_bounds",
        description="Accessing an array or sequence element at an index that equals or exceeds its length.",
        pedagogical_nudge_example="Remember that 0-indexed sequences end at length minus 1. Which index is your loop accessing?",
    ),
    BugCategory.WRONG_OPERATOR: CategoryMetadata(
        category=BugCategory.WRONG_OPERATOR,
        display_name="Wrong Operator or Condition",
        concept="conditional_logic",
        description="Using the incorrect comparison or assignment in place of equality.",
        pedagogical_nudge_example="Read the condition out loud. Under what exact circumstance should this branch execute?",
    ),
    BugCategory.MISSING_RETURN: CategoryMetadata(
        category=BugCategory.MISSING_RETURN,
        display_name="Missing Return Value",
        concept="functions_and_returns",
        description="Function computes a result but terminates without returning it to the caller.",
        pedagogical_nudge_example="Does your function explicitly pass the calculated result back to whoever called it?",
    ),
    BugCategory.LOOP_BOUNDARY: CategoryMetadata(
        category=BugCategory.LOOP_BOUNDARY,
        display_name="Loop Boundary / Infinite Loop",
        concept="iteration_and_termination",
        description="Loop condition never becomes false or increment/decrement step is incorrect.",
        pedagogical_nudge_example="What changes during each iteration that guarantees the loop will eventually terminate?",
    ),
    BugCategory.WRONG_VARIABLE: CategoryMetadata(
        category=BugCategory.WRONG_VARIABLE,
        display_name="Wrong Variable Referenced",
        concept="identifier_binding",
        description="Referencing the outer or wrong variable name instead of the intended parameter or loop variable.",
        pedagogical_nudge_example="Check whether the variable updated in the loop matches the one you inspect after.",
    ),
}


def get_category_metadata(category: BugCategory) -> Optional[CategoryMetadata]:
    """Retrieve metadata and pedagogical concept for a given bug category."""
    return CATEGORY_DEFINITIONS.get(category)
