from typing import Dict, List
from pydantic import BaseModel, Field
from app.categories import BugCategory


class WorkedExample(BaseModel):
    id: str
    category: BugCategory
    title: str
    problem_description: str
    code: str
    explanation: str


WORKED_EXAMPLES: List[WorkedExample] = [
    # 1. Syntax Error
    WorkedExample(
        id="ex_syntax_colon",
        category=BugCategory.SYNTAX_ERROR,
        title="Valid block headers and terminating colons",
        problem_description="Calculating discounted price if customer is a member",
        code="""def apply_discount(price, is_member):
    # Every if, for, while, and def header statement MUST end with a colon (:)
    if is_member:
        return price * 0.9
    else:
        return price""",
        explanation="In Python, colons tell the interpreter that an indented compound statement block begins on the next line. Missing colons prevent Python from recognizing the block structure.",
    ),
    # 2. Undefined Name
    WorkedExample(
        id="ex_undefined_name",
        category=BugCategory.UNDEFINED_NAME,
        title="Declaring and evaluating identifiers",
        problem_description="Tracking user score across rounds",
        code="""def update_score(current_score, points):
    # 'bonus' is explicitly declared and initialized before use
    bonus = 10
    new_total = current_score + points + bonus
    return new_total""",
        explanation="Variables must be spelled identically everywhere they are used. Declaring and assigning a variable before evaluating it avoids NameError exceptions.",
    ),
    # 3. Type Error
    WorkedExample(
        id="ex_type_conversion",
        category=BugCategory.TYPE_ERROR,
        title="Explicit type conversion between strings and numbers",
        problem_description="Formatting transaction receipt output",
        code="""def format_receipt(item_name, price):
    # Convert numeric price to str before concatenating with text
    price_str = str(price)
    return "Item: " + item_name + ", Price: $" + price_str""",
        explanation="Python is strongly typed and will not automatically cast numbers to strings when concatenating with '+'. Use str(value) or f-strings to format different data types safely.",
    ),
    # 4. Index Out of Range
    WorkedExample(
        id="ex_index_bounds",
        category=BugCategory.INDEX_OUT_OF_RANGE,
        title="Safe list boundary traversal",
        problem_description="Accessing elements in a shopping list",
        code="""def get_last_item(items):
    if not items:
        return None
    # 0-indexed sequences end at len(items) - 1, not len(items)
    last_index = len(items) - 1
    return items[last_index]""",
        explanation="A list of length N has valid indices from 0 up to N - 1. Accessing items[len(items)] attempts to read one element beyond the list boundary, triggering IndexError.",
    ),
    # 5. Wrong Operator
    WorkedExample(
        id="ex_wrong_operator",
        category=BugCategory.WRONG_OPERATOR,
        title="Equality comparison vs assignment in conditionals",
        problem_description="Checking user authorization role",
        code="""def check_admin(role):
    # Use '==' to test for equality, '=' is for assignment
    if role == "administrator":
        return True
    return False""",
        explanation="Conditional expressions require comparison operators (==, !=, <, >). Using a single '=' attempts variable assignment, which is a syntax error inside standard conditional checks.",
    ),
    # 6. Missing Return
    WorkedExample(
        id="ex_missing_return",
        category=BugCategory.MISSING_RETURN,
        title="Passing calculated results back via return",
        problem_description="Calculating rectangle area",
        code="""def calculate_area(width, height):
    area = width * height
    # Explicitly return the calculated value to the caller
    return area""",
        explanation="Functions that compute a value must explicitly use the 'return' statement. Without 'return', Python finishes execution and automatically returns 'None' to whoever called the function.",
    ),
    # 7. Loop Boundary
    WorkedExample(
        id="ex_loop_boundary",
        category=BugCategory.LOOP_BOUNDARY,
        title="Loop state progression and termination",
        problem_description="Countdown sequence before rocket launch",
        code="""def countdown(seconds):
    current = seconds
    while current > 0:
        print(f"{current}...")
        # State variable MUST decrement toward the stopping condition (0)
        current -= 1
    print("Liftoff!")""",
        explanation="Every loop must update its control variable on each iteration toward its stopping condition. If the state never advances, the condition remains true indefinitely, causing an infinite loop.",
    ),
    # 8. Wrong Variable
    WorkedExample(
        id="ex_wrong_variable",
        category=BugCategory.WRONG_VARIABLE,
        title="Referencing loop item inside accumulator",
        problem_description="Summing temperatures over a week",
        code="""def average_temperature(temperatures):
    total = 0
    # 'temp' is the current item being processed in the loop
    for temp in temperatures:
        total += temp
    return total / len(temperatures) if temperatures else 0""",
        explanation="Be vigilant when naming loop variables. Accidentally referencing an outer list name or global identifier instead of the iteration variable causes calculation bugs.",
    ),
]


def get_examples_by_category(category: BugCategory) -> List[WorkedExample]:
    return [ex for ex in WORKED_EXAMPLES if ex.category == category]
