"""
SocraCode Canonical Hint Templates for C++ (Levels 1 to 3).
Rules:
- Level 1 (Nudge): Guiding question prompting code re-reading. NO code, NO names of fixes.
- Level 2 (Concept): Names the computer science concept in C++. NO code.
- Level 3 (Location): Pinpoints problem area and line number. NO corrected code.
"""

from typing import Dict
from app.categories import BugCategory

HINT_TEMPLATES_CPP: Dict[BugCategory, Dict[int, str]] = {
    BugCategory.SYNTAX_ERROR: {
        1: "Take a close look at the punctuation and structural delimiters in your C++ code. Are all statement terminators, braces, and parentheses properly closed?",
        2: "This is a Syntax error related to C++ grammar. Every statement must terminate with a semicolon, and control blocks require matching braces.",
        3: "Look closely at line {line_number}. Check the end of this statement or the line directly preceding it for a missing semicolon or unmatched bracket.",
    },
    BugCategory.UNDEFINED_NAME: {
        1: "Are all variable, function, and type names spelled exactly as where you declared or included them?",
        2: "This involves Identifier Scope and Declaration in C++. In C++, every variable and function must be declared before its first point of use.",
        3: "Look closely at line {line_number}. The compiler reports that '{undefined_name}' was not declared in this scope. Check for a typo or verify that the header or declaration is included.",
    },
    BugCategory.TYPE_ERROR: {
        1: "What type of data does each operand hold, and does C++ permit direct assignment or operation between them without conversion?",
        2: "This is a Static Type and Conversion concept in C++. C++ strictly enforces type compatibility between operands and function parameter signatures.",
        3: "Look closely at line {line_number}. An operation or assignment is being performed on incompatible types. Check whether a cast or type conversion is required.",
    },
    BugCategory.INDEX_OUT_OF_RANGE: {
        1: "What are the valid starting and ending indices for this array or vector?",
        2: "This is a Buffer Bounds and Memory Access concept in C++. In C++, valid array indices run from 0 to size - 1. Accessing index size causes undefined behaviour or a segmentation fault.",
        3: "Look closely at line {line_number}. The index accessed exceeds the bounds of the array or vector. Check loop condition bounds (such as '<' versus '<=').",
    },
    BugCategory.WRONG_OPERATOR: {
        1: "Read your conditional expression carefully. Are you checking for equivalence or accidentally assigning a value?",
        2: "This relates to C++ Relational and Logical Operators. Remember that '==' tests equality, whereas '=' assigns a value.",
        3: "Look closely at line {line_number}. Inspect the comparison or logical operator used in this expression to ensure it reflects your intended logic.",
    },
    BugCategory.MISSING_RETURN: {
        1: "When a function computes a value, how does that computed result get handed back along every execution branch?",
        2: "This is a Function Return Value concept in C++. A non-void function must supply a value of the declared type along all execution paths.",
        3: "Look closely at line {line_number} and the closing brace of your function. Ensure every branch supplies the required result type before finishing.",
    },
    BugCategory.LOOP_BOUNDARY: {
        1: "What condition terminates your loop, and how does each iteration advance toward satisfying that condition?",
        2: "This is an Iteration Invariant and Loop Termination concept. Every while or for loop must update its control variable to reach the termination condition.",
        3: "Look closely at line {line_number}, where the loop begins. Check that loop variables are updated inside the loop body.",
    },
    BugCategory.WRONG_VARIABLE: {
        1: "Check each identifier inside your loop or calculation. Are you modifying the exact variable you intend to use in the following lines?",
        2: "This relates to Variable Shadowing and Name Lookup in C++. Using an outer or similarly named variable instead of a local variable can corrupt calculation state.",
        3: "Look closely at line {line_number}. Verify that the variable being accessed is the intended parameter or loop variable.",
    },
}


def get_template_cpp(category: BugCategory, level: int) -> str:
    category_templates = HINT_TEMPLATES_CPP.get(category, HINT_TEMPLATES_CPP[BugCategory.SYNTAX_ERROR])
    return category_templates.get(level, category_templates[1])
