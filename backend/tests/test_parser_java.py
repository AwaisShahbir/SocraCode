import pytest
from app.parser.java_parser import JavaErrorParser


def test_java_parser_syntax_error_missing_semicolon():
    parser = JavaErrorParser()
    code = """public class Solution {
    public static void main(String[] args) {
        int x = 42
    }
}"""
    stderr = """Solution.java:3: error: ';' expected
        int x = 42
                  ^
1 error"""
    parsed = parser.parse(code, stderr)
    assert parsed.has_error is True
    assert parsed.error_type == "SyntaxError"
    assert parsed.line_number == 3
    assert "';' expected" in parsed.message


def test_java_parser_name_error_cannot_find_symbol():
    parser = JavaErrorParser()
    code = """public class Solution {
    public static void main(String[] args) {
        System.out.println(myScore);
    }
}"""
    stderr = """Solution.java:3: error: cannot find symbol
        System.out.println(myScore);
                           ^
  symbol:   variable myScore
  location: class Solution
1 error"""
    parsed = parser.parse(code, stderr)
    assert parsed.has_error is True
    assert parsed.error_type == "NameError"
    assert parsed.line_number == 3
    assert "cannot find symbol" in parsed.message


def test_java_parser_runtime_index_out_of_bounds():
    parser = JavaErrorParser()
    code = """public class Solution {
    public static void main(String[] args) {
        int[] arr = {1, 2, 3};
        System.out.println(arr[5]);
    }
}"""
    stderr = """Exception in thread "main" java.lang.ArrayIndexOutOfBoundsException: Index 5 out of bounds for length 3
	at Solution.main(Solution.java:4)"""
    parsed = parser.parse(code, stderr)
    assert parsed.has_error is True
    assert parsed.error_type == "ArrayIndexOutOfBoundsException"
    assert parsed.line_number == 4
    assert "Index 5 out of bounds" in parsed.message


def test_java_parser_timeout():
    parser = JavaErrorParser()
    parsed = parser.parse("code", "", timed_out=True)
    assert parsed.has_error is True
    assert parsed.error_type == "TimeoutError"
