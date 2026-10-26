import pytest
from app.categories import BugCategory
from app.parser.python_parser import ParsedError
from app.rules import match_rules


def test_java_rules_syntax_missing_semicolon():
    code = """public class Solution {
    public static void main(String[] args) {
        int val = 100
    }
}"""
    err = ParsedError(
        has_error=True,
        error_type="SyntaxError",
        message="';' expected",
        line_number=3,
        code_line="        int val = 100",
    )
    match = match_rules("java", code, err)
    assert match.category == BugCategory.SYNTAX_ERROR
    assert match.line_number == 3
    assert match.confidence >= 0.9


def test_java_rules_undefined_name_typo():
    code = """public class Solution {
    public static void main(String[] args) {
        int totalScore = 50;
        System.out.println(totlScore);
    }
}"""
    err = ParsedError(
        has_error=True,
        error_type="NameError",
        message="cannot find symbol; symbol: variable totlScore",
        line_number=4,
        code_line="        System.out.println(totlScore);",
    )
    match = match_rules("java", code, err)
    assert match.category == BugCategory.UNDEFINED_NAME
    assert match.line_number == 4
    assert match.context.get("suggested_name") == "totalScore"


def test_java_rules_timeout_loop():
    code = """public class Solution {
    public static void main(String[] args) {
        int i = 0;
        while (i < 10) {
            // Missing increment
        }
    }
}"""
    err = ParsedError(has_error=True, error_type="TimeoutError", message="Timed out", line_number=1)
    match = match_rules("java", code, err)
    assert match.category == BugCategory.LOOP_BOUNDARY
    assert match.line_number == 4


def test_cpp_rules_syntax_missing_semicolon():
    code = """#include <iostream>
int main() {
    int a = 10
    return 0;
}"""
    err = ParsedError(
        has_error=True,
        error_type="SyntaxError",
        message="expected ';' before 'return'",
        line_number=3,
        code_line="    int a = 10",
    )
    match = match_rules("cpp", code, err)
    assert match.category == BugCategory.SYNTAX_ERROR
    assert match.line_number == 3
    assert match.confidence >= 0.9


def test_cpp_rules_undefined_name_typo():
    code = """#include <iostream>
int main() {
    int maxLimit = 100;
    std::cout << mxLimit << std::endl;
    return 0;
}"""
    err = ParsedError(
        has_error=True,
        error_type="NameError",
        message="'mxLimit' was not declared in this scope",
        line_number=4,
        code_line="    std::cout << mxLimit << std::endl;",
    )
    match = match_rules("cpp", code, err)
    assert match.category == BugCategory.UNDEFINED_NAME
    assert match.line_number == 4
    assert match.context.get("suggested_name") == "maxLimit"


def test_cpp_rules_index_out_of_bounds_segfault():
    code = """#include <vector>
int main() {
    std::vector<int> v = {1, 2};
    return v[10];
}"""
    err = ParsedError(
        has_error=True,
        error_type="SegmentationFault",
        message="Memory access violation",
        line_number=1,
    )
    match = match_rules("cpp", code, err)
    assert match.category == BugCategory.INDEX_OUT_OF_RANGE
