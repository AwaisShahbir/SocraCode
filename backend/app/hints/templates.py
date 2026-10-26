"""
SocraCode Canonical Hint Templates for Python (Levels 1 to 3).
Rules:
- Level 1 (Nudge): Guiding question prompting code re-reading. NO code, NO names of fixes.
- Level 2 (Concept): Names the computer science concept. NO code.
- Level 3 (Location): Pinpoints problem area and line number. NO corrected code.
"""

from typing import Dict
from app.categories import BugCategory


# Templates indexed by: (BugCategory, Level)
HINT_TEMPLATES_PYTHON: Dict[BugCategory, Dict[int, str]] = {
    BugCategory.SYNTAX_ERROR: {
        1: "Take a close look at the punctuation and structural symbols in your code. Are all statement blocks, brackets, and colons properly paired and closed?",
        2: "This is a Syntax error related to Python's grammatical structure. Python relies on specific terminating punctuation, such as colons after header statements and matched parentheses.",
        3: "Look closely at line {line_number}. Check the very end of this statement or the preceding line for a missing colon or unmatched delimiter.",
    },
    BugCategory.UNDEFINED_NAME: {
        1: "Are all the variable and function names you are reading spelled exactly the same way as where you first defined or assigned them?",
        2: "This involves Variable Scope and Declaration. In Python, every identifier must be declared and assigned before it can be read or evaluated.",
        3: "Look closely at line {line_number}. The identifier '{undefined_name}' is being referenced before Python knows what value it holds. Check for a spelling discrepancy or missing prior assignment.",
    },
    BugCategory.TYPE_ERROR: {
        1: "What type of data does each variable or operand hold at this step of the calculation? Can those two types be combined directly?",
        2: "This is a Data Type incompatibility error. Certain operations are only valid between compatible types, such as numbers with numbers or strings with strings.",
        3: "Look closely at line {line_number}. An operation is being attempted on values of incompatible types. Consider whether one of the values needs type conversion before being combined.",
    },
    BugCategory.INDEX_OUT_OF_RANGE: {
        1: "How many items are in the collection, and what are the valid starting and ending index numbers when indexing items?",
        2: "This is an Indexing and Sequence Bounds error. Remember that sequence indexing starts at position 0 and ends at total length minus 1.",
        3: "Look closely at line {line_number}. The index being accessed exceeds the boundaries of the list or sequence. Check the loop range bounds or the index offset calculation.",
    },
    BugCategory.WRONG_OPERATOR: {
        1: "Read your conditional expression aloud. Under what exact condition should this branch execute versus being skipped?",
        2: "This relates to Conditional Logic and Comparison Operators. In Python, double equals checks for equality, while a single equals performs an assignment.",
        3: "Look closely at line {line_number}. Inspect the comparison operator or relational expression used in this condition to ensure it reflects your intended logic.",
    },
    BugCategory.MISSING_RETURN: {
        1: "When a function calculates a value, how does that calculated result get passed back to the rest of your program?",
        2: "This is a Functions and Return Values concept. If a function finishes executing its statements without explicitly passing a value back, it evaluates to None.",
        3: "Look closely at line {line_number} and the end of your function body. Ensure the calculated result is explicitly passed back to the caller.",
    },
    BugCategory.LOOP_BOUNDARY: {
        1: "What guarantees that your loop will eventually finish running? What variable changes on every iteration toward the stopping condition?",
        2: "This is an Iteration and Loop Termination concept. Every while or recursive loop must make steady progress toward a terminal condition.",
        3: "Look closely at line {line_number}, where the loop begins. Check that the condition can be satisfied and that loop state variables are updated within the loop body.",
    },
    BugCategory.WRONG_VARIABLE: {
        1: "Check every variable inside your loop or expression. Is the variable being updated the exact same one you intend to use in subsequent lines?",
        2: "This relates to Identifier Binding and Variable Shadowing. Using an outer variable when a local loop variable is intended can cause unexpected calculations.",
        3: "Look closely at line {line_number}. Check whether you are referencing the parameter or loop variable, rather than an unrelated variable of a similar name.",
    },
}


def get_template(category: BugCategory, level: int) -> str:
    """Retrieve raw template for category and level."""
    category_templates = HINT_TEMPLATES_PYTHON.get(category, HINT_TEMPLATES_PYTHON[BugCategory.SYNTAX_ERROR])
    return category_templates.get(
        level,
        "Review your code structure and logic carefully. What does the current line of code expect?",
    )
