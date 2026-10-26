from app.runner.local_runner import LocalSubprocessRunner

def test_local_runner_java_success():
    runner = LocalSubprocessRunner()
    code = """public class Solution {
    public static void main(String[] args) {
        System.out.println("Hello from SocraCode Java!");
    }
}"""
    result = runner.run_java(code)
    assert result.exit_code == 0
    assert "Hello from SocraCode Java!" in result.stdout
    assert result.timed_out is False


def test_local_runner_java_syntax_error():
    runner = LocalSubprocessRunner()
    # Missing semicolon
    code = """public class Solution {
    public static void main(String[] args) {
        System.out.println("Missing semi")
    }
}"""
    result = runner.run_java(code)
    assert result.exit_code != 0
    assert "error: ';' expected" in result.stderr
