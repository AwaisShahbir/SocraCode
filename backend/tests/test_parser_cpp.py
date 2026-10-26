import pytest
from app.parser.cpp_parser import CppErrorParser


def test_cpp_parser_syntax_error_missing_semicolon():
    parser = CppErrorParser()
    code = """#include <iostream>
int main() {
    int x = 42
    return 0;
}"""
    stderr = """solution.cpp:3:15: error: expected ';' before 'return'
    int x = 42
              ^
              ;
    return 0;"""
    parsed = parser.parse(code, stderr)
    assert parsed.has_error is True
    assert parsed.error_type == "SyntaxError"
    assert parsed.line_number == 3
    assert "expected ';'" in parsed.message


def test_cpp_parser_undefined_identifier():
    parser = CppErrorParser()
    code = """#include <iostream>
int main() {
    std::cout << counter << std::endl;
    return 0;
}"""
    stderr = """solution.cpp:3:18: error: 'counter' was not declared in this scope
    std::cout << counter << std::endl;
                 ^~~~~~~"""
    parsed = parser.parse(code, stderr)
    assert parsed.has_error is True
    assert parsed.error_type == "NameError"
    assert parsed.line_number == 3
    assert "was not declared in this scope" in parsed.message


def test_cpp_parser_segmentation_fault():
    parser = CppErrorParser()
    code = """#include <iostream>
int main() {
    int* p = nullptr;
    *p = 10;
}"""
    stderr = "Segmentation fault (core dumped)"
    parsed = parser.parse(code, stderr)
    assert parsed.has_error is True
    assert parsed.error_type == "SegmentationFault"
    assert "Memory access violation" in parsed.message


def test_cpp_parser_timeout():
    parser = CppErrorParser()
    parsed = parser.parse("code", "", timed_out=True)
    assert parsed.has_error is True
    assert parsed.error_type == "TimeoutError"
