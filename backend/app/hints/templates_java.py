"""
SocraCode Canonical Hint Templates for Java (Levels 1 to 3).
Rules:
- Level 1 (Nudge): Guiding question prompting code re-reading. NO code, NO names of fixes.
- Level 2 (Concept): Names the computer science concept in Java. NO code.
- Level 3 (Location): Pinpoints problem area and line number. NO corrected code.
"""

from typing import Dict
from app.categories import BugCategory

HINT_TEMPLATES_JAVA: Dict[BugCategory, Dict[int, str]] = {
    BugCategory.SYNTAX_ERROR: {
        1: "Take a close look at the punctuation and structural symbols in your Java code. Are all statement terminators, braces, and parentheses properly closed?",
        2: "This is a Syntax error related to Java's grammar. Java requires statements to be terminated with semicolons and code blocks enclosed in matching braces.",
        3: "Look closely at line {line_number}. Check the end of this statement for a missing semicolon or an unmatched delimiter.",
    },
    BugCategory.UNDEFINED_NAME: {
        1: "Are all the variable, class, and method names you are referencing spelled exactly as where you declared them?",
        2: "This involves Variable Declaration and Scope in Java. In Java, every identifier must have a declared type and be in scope before it can be used.",
        3: "Look closely at line {line_number}. The compiler cannot find the symbol '{undefined_name}'. Check for a spelling mistake or verify that the variable is declared and accessible in this scope.",
    },
    BugCategory.TYPE_ERROR: {
        1: "What data type is expected by the variable or method parameter, and what type is actually being supplied?",
        2: "This is a Static Type Safety concept in Java. Java is strongly typed; assigning a value to a variable of an incompatible type requires explicit casting or conversion.",
        3: "Look closely at line {line_number}. The types involved in this assignment or expression are incompatible. Consider converting the value to the required target type.",
    },
    BugCategory.INDEX_OUT_OF_RANGE: {
        1: "What is the size of the array, and what are the valid first and last index positions?",
        2: "This is an Array Bounds and Zero-Based Indexing concept. In Java, valid indices range from 0 to array.length - 1. Accessing index array.length throws an ArrayIndexOutOfBoundsException.",
        3: "Look closely at line {line_number}. The array index accessed is outside the valid range [0, length - 1]. Check your loop bounds or index offset.",
    },
    BugCategory.WRONG_OPERATOR: {
        1: "Read your conditional expression carefully. Are you comparing values or attempting an assignment?",
        2: "This relates to Java Boolean Expressions and Comparison Operators. In Java, '==' checks equality while '=' performs assignment. Furthermore, Strings are compared using the equals method.",
        3: "Look closely at line {line_number}. Inspect the relational or logical operator used in this expression to ensure it reflects your intended comparison.",
    },
    BugCategory.MISSING_RETURN: {
        1: "When a method computes a value, how does that computed outcome get handed back along every execution branch?",
        2: "This is a Method Return Types concept in Java. A non-void method must supply a value matching its declared signature along every possible branch.",
        3: "Look closely at line {line_number} and the closing brace of your method. Ensure every code branch supplies the declared result before concluding.",
    },
    BugCategory.LOOP_BOUNDARY: {
        1: "What variable controls loop termination, and how does it advance toward the exit condition on each iteration?",
        2: "This is an Iteration and Loop Invariant concept. A while loop or for loop must update its control variable during each iteration to avoid running indefinitely.",
        3: "Look closely at line {line_number}, where the loop begins. Check that loop control variables are updated inside the loop body.",
    },
    BugCategory.WRONG_VARIABLE: {
        1: "Inspect the variables used in this statement. Are you referencing the local parameter or an instance variable of a similar name?",
        2: "This involves Variable Shadowing and Identifier Resolution in Java. Using an outer or similarly named variable instead of the intended parameter can produce incorrect state.",
        3: "Look closely at line {line_number}. Verify that the variable being accessed or modified is the one you intended to use.",
    },
}


def get_template_java(category: BugCategory, level: int) -> str:
    category_templates = HINT_TEMPLATES_JAVA.get(category, HINT_TEMPLATES_JAVA[BugCategory.SYNTAX_ERROR])
    return category_templates.get(level, category_templates[1])
