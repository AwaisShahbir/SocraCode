from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from app.categories import BugCategory


class WorkedExample(BaseModel):
    id: str
    language: str = Field(default="python", description="Language of worked example: python, java, cpp")
    category: BugCategory
    title: str
    problem_description: str
    code: str
    explanation: str


WORKED_EXAMPLES: List[WorkedExample] = [
    # ==========================================
    # PYTHON WORKED EXAMPLES
    # ==========================================
    WorkedExample(
        id="ex_syntax_colon",
        language="python",
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
    WorkedExample(
        id="ex_undefined_name",
        language="python",
        category=BugCategory.UNDEFINED_NAME,
        title="Declaring and evaluating identifiers",
        problem_description="Tracking user score across rounds",
        code="""def update_score(current_score, points):
    bonus = 10
    new_total = current_score + points + bonus
    return new_total""",
        explanation="Variables must be spelled identically everywhere they are used. Declaring and assigning a variable before evaluating it avoids NameError exceptions.",
    ),
    WorkedExample(
        id="ex_type_conversion",
        language="python",
        category=BugCategory.TYPE_ERROR,
        title="Explicit type conversion between strings and numbers",
        problem_description="Formatting transaction receipt output",
        code="""def format_receipt(item_name, price):
    price_str = str(price)
    return "Item: " + item_name + ", Price: $" + price_str""",
        explanation="Python is strongly typed and will not automatically cast numbers to strings when concatenating with '+'. Use str(value) or f-strings to format different data types safely.",
    ),
    WorkedExample(
        id="ex_index_bounds",
        language="python",
        category=BugCategory.INDEX_OUT_OF_RANGE,
        title="Safe list boundary traversal",
        problem_description="Accessing elements in a shopping list",
        code="""def get_last_item(items):
    if not items:
        return None
    last_index = len(items) - 1
    return items[last_index]""",
        explanation="A list of length N has valid indices from 0 up to N - 1. Accessing items[len(items)] attempts to read one element beyond the list boundary, triggering IndexError.",
    ),
    WorkedExample(
        id="ex_wrong_operator",
        language="python",
        category=BugCategory.WRONG_OPERATOR,
        title="Equality comparison vs assignment in conditionals",
        problem_description="Checking user authorization role",
        code="""def check_admin(role):
    if role == "administrator":
        return True
    return False""",
        explanation="Conditional expressions require comparison operators (==, !=, <, >). Using a single '=' attempts variable assignment, which is a syntax error inside standard conditional checks.",
    ),
    WorkedExample(
        id="ex_missing_return",
        language="python",
        category=BugCategory.MISSING_RETURN,
        title="Passing calculated results back via return",
        problem_description="Calculating rectangle area",
        code="""def calculate_area(width, height):
    area = width * height
    return area""",
        explanation="Functions that compute a value must explicitly use the 'return' statement. Without 'return', Python finishes execution and automatically returns 'None' to whoever called the function.",
    ),
    WorkedExample(
        id="ex_loop_boundary",
        language="python",
        category=BugCategory.LOOP_BOUNDARY,
        title="Loop state progression and termination",
        problem_description="Countdown sequence before rocket launch",
        code="""def countdown(seconds):
    current = seconds
    while current > 0:
        print(f"{current}...")
        current -= 1
    print("Liftoff!")""",
        explanation="Every loop must update its control variable on each iteration toward its stopping condition. If the state never advances, the condition remains true indefinitely, causing an infinite loop.",
    ),
    WorkedExample(
        id="ex_wrong_variable",
        language="python",
        category=BugCategory.WRONG_VARIABLE,
        title="Referencing loop item inside accumulator",
        problem_description="Summing temperatures over a week",
        code="""def average_temperature(temperatures):
    total = 0
    for temp in temperatures:
        total += temp
    return total / len(temperatures) if temperatures else 0""",
        explanation="Be vigilant when naming loop variables. Accidentally referencing an outer list name or global identifier instead of the iteration variable causes calculation bugs.",
    ),

    # ==========================================
    # JAVA WORKED EXAMPLES
    # ==========================================
    WorkedExample(
        id="ex_java_syntax_semicolon",
        language="java",
        category=BugCategory.SYNTAX_ERROR,
        title="Terminating statements with semicolons in Java",
        problem_description="Greeting a user by name",
        code="""public class Greeter {
    public static void greet(String name) {
        // Every Java statement must end with a semicolon (;)
        System.out.println("Welcome, " + name);
    }
}""",
        explanation="In Java, semicolons explicitly terminate expressions. Omitting a semicolon at the end of a line produces a compile-time '; expected' error.",
    ),
    WorkedExample(
        id="ex_java_undefined_name",
        language="java",
        category=BugCategory.UNDEFINED_NAME,
        title="Declaring variables with types before evaluation",
        problem_description="Tracking user visit count",
        code="""public class VisitorCounter {
    public static int incrementVisits(int initialVisits) {
        // Explicitly declare type and initial value before referencing
        int additionalVisits = 5;
        return initialVisits + additionalVisits;
    }
}""",
        explanation="Java requires all variables to be explicitly declared with a type and initialized before they can be read. Check for spelling mismatches or missing declarations.",
    ),
    WorkedExample(
        id="ex_java_type_error",
        language="java",
        category=BugCategory.TYPE_ERROR,
        title="Parsing strings to integers safely",
        problem_description="Converting user text input to an integer",
        code="""public class ParserUtil {
    public static int parseAge(String input) {
        // Convert String to primitive int using Integer.parseInt
        int age = Integer.parseInt(input);
        return age;
    }
}""",
        explanation="Java is statically typed and will not implicitly convert a String into a numeric int. Use Integer.parseInt(str) or String.valueOf(num) for safe conversion.",
    ),
    WorkedExample(
        id="ex_java_index_bounds",
        language="java",
        category=BugCategory.INDEX_OUT_OF_RANGE,
        title="Valid 0-indexed array boundaries in Java",
        problem_description="Reading the last score from an integer array",
        code="""public class ScoreKeeper {
    public static int getLastScore(int[] scores) {
        if (scores.length == 0) return -1;
        // The last element is at scores.length - 1, not scores.length
        return scores[scores.length - 1];
    }
}""",
        explanation="Java arrays are 0-indexed: valid indices range from 0 to length - 1. Accessing scores[scores.length] causes an ArrayIndexOutOfBoundsException.",
    ),
    WorkedExample(
        id="ex_java_wrong_operator",
        language="java",
        category=BugCategory.WRONG_OPERATOR,
        title="String equality comparison using .equals()",
        problem_description="Verifying user permissions",
        code="""public class AuthCheck {
    public static boolean isAdmin(String role) {
        // In Java, object strings are compared with .equals(), not '=='
        return "admin".equals(role);
    }
}""",
        explanation="In Java, '==' checks reference memory identity, not string content. Always compare string contents using string1.equals(string2).",
    ),
    WorkedExample(
        id="ex_java_missing_return",
        language="java",
        category=BugCategory.MISSING_RETURN,
        title="Returning declared types on all code branches",
        problem_description="Calculating maximum of two numbers",
        code="""public class MathUtil {
    public static int findMax(int a, int b) {
        if (a > b) {
            return a;
        } else {
            return b;
        }
    }
}""",
        explanation="A non-void Java method must provide a return statement on every conceivable execution branch. If a branch fails to return, the compiler flags a 'missing return statement'.",
    ),
    WorkedExample(
        id="ex_java_loop_boundary",
        language="java",
        category=BugCategory.LOOP_BOUNDARY,
        title="Advancing loop control variables toward termination",
        problem_description="Printing countdown numbers",
        code="""public class Countdown {
    public static void run(int start) {
        int count = start;
        while (count > 0) {
            System.out.println(count);
            // Decrement state variable toward 0
            count--;
        }
    }
}""",
        explanation="A while loop must modify its control variable within the loop body. If the control variable is never updated, the condition remains true forever.",
    ),
    WorkedExample(
        id="ex_java_wrong_variable",
        language="java",
        category=BugCategory.WRONG_VARIABLE,
        title="Loop accumulator using the iteration variable",
        problem_description="Summing numbers in an array",
        code="""public class Summer {
    public static int sumArray(int[] numbers) {
        int sum = 0;
        for (int num : numbers) {
            sum += num;
        }
        return sum;
    }
}""",
        explanation="Ensure you accumulate using the loop variable 'num' rather than an unrelated outer variable.",
    ),

    # ==========================================
    # C++ WORKED EXAMPLES
    # ==========================================
    WorkedExample(
        id="ex_cpp_syntax_semicolon",
        language="cpp",
        category=BugCategory.SYNTAX_ERROR,
        title="Terminating statements with semicolons in C++",
        problem_description="Outputting greeting message to stdout",
        code="""#include <iostream>
#include <string>

void greet(const std::string& name) {
    // Every statement in C++ must conclude with a semicolon (;)
    std::cout << "Hello, " << name << std::endl;
}""",
        explanation="In C++, statements must end with a semicolon. Missing semicolons before subsequent statements cause 'expected ; before return' compiler errors.",
    ),
    WorkedExample(
        id="ex_cpp_undefined_name",
        language="cpp",
        category=BugCategory.UNDEFINED_NAME,
        title="Declaring identifiers before use in C++",
        problem_description="Calculating discounted total price",
        code="""#include <iostream>

double calculate_price(double base_price) {
    // Identifier declared with type before use
    double discount_rate = 0.15;
    return base_price * (1.0 - discount_rate);
}""",
        explanation="C++ requires all variables and functions to be declared in scope before they are evaluated. Check spelling or add the declaration above the use site.",
    ),
    WorkedExample(
        id="ex_cpp_type_error",
        language="cpp",
        category=BugCategory.TYPE_ERROR,
        title="Converting string to integer with std::stoi",
        problem_description="Converting command line parameter to number",
        code="""#include <string>

int parse_port(const std::string& port_str) {
    // Explicit conversion from std::string to int
    int port = std::stoi(port_str);
    return port;
}""",
        explanation="C++ does not automatically cast strings to integer numbers. Use std::stoi(str) or stringstream for explicit type conversions.",
    ),
    WorkedExample(
        id="ex_cpp_index_bounds",
        language="cpp",
        category=BugCategory.INDEX_OUT_OF_RANGE,
        title="Valid std::vector boundaries in C++",
        problem_description="Accessing the back element of a vector",
        code="""#include <vector>

int get_last_element(const std::vector<int>& items) {
    if (items.empty()) return -1;
    // Valid indices run from 0 to items.size() - 1
    return items[items.size() - 1];
}""",
        explanation="Accessing items[items.size()] attempts an out-of-bounds memory read, leading to undefined behavior or segmentation faults. Alternatively, use items.back().",
    ),
    WorkedExample(
        id="ex_cpp_wrong_operator",
        language="cpp",
        category=BugCategory.WRONG_OPERATOR,
        title="Equality comparison (==) vs assignment (=) in C++",
        problem_description="Validating server connection status",
        code="""bool is_connected(int status) {
    // '==' compares values, '=' assigns
    if (status == 200) {
        return true;
    }
    return false;
}""",
        explanation="Using a single '=' inside an if condition assigns the value rather than testing equality. Always use '==' for equivalence checks.",
    ),
    WorkedExample(
        id="ex_cpp_missing_return",
        language="cpp",
        category=BugCategory.MISSING_RETURN,
        title="Returning values from non-void C++ functions",
        problem_description="Computing square of an integer",
        code="""int square(int n) {
    int result = n * n;
    // Explicit return required for non-void function
    return result;
}""",
        explanation="A non-void C++ function that finishes without returning a value causes undefined behavior and compiler warnings: 'control reaches end of non-void function'.",
    ),
    WorkedExample(
        id="ex_cpp_loop_boundary",
        language="cpp",
        category=BugCategory.LOOP_BOUNDARY,
        title="Advancing loop state toward termination in C++",
        problem_description="Countdown while loop",
        code="""#include <iostream>

void countdown(int start) {
    int i = start;
    while (i > 0) {
        std::cout << i << std::endl;
        // Decrement towards 0
        i--;
    }
}""",
        explanation="Every loop must decrement or advance its counter toward the stopping condition. If the state never changes, the condition stays true indefinitely.",
    ),
    WorkedExample(
        id="ex_cpp_wrong_variable",
        language="cpp",
        category=BugCategory.WRONG_VARIABLE,
        title="Range-based for loop accumulator in C++",
        problem_description="Summing elements of a vector",
        code="""#include <vector>

int sum_elements(const std::vector<int>& data) {
    int total = 0;
    for (int value : data) {
        total += value;
    }
    return total;
}""",
        explanation="Ensure you accumulate using the loop variable 'value' rather than referencing the container name.",
    ),
]


def get_examples_by_category(category: BugCategory, language: str = "python") -> List[WorkedExample]:
    norm_lang = language.lower().strip()
    if norm_lang == "c++":
        norm_lang = "cpp"
    matching = [ex for ex in WORKED_EXAMPLES if ex.category == category and ex.language == norm_lang]
    if matching:
        return matching
    # Fallback to python examples if language specific ones not found
    return [ex for ex in WORKED_EXAMPLES if ex.category == category]
