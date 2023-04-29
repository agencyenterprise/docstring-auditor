import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from docstring_auditor.main import docstring_auditor, apply_solution


def test_docstring_auditor_auto_fix(tmp_path):
    # Create a temporary Python file with a sample function
    sample_code = '''
def sample_function(x, y):
    """
    Subtract two numbers together.
    """
    return x + y
'''
    temp_file = tmp_path / "sample.py"
    temp_file.write_text(sample_code)

    # Mock the ask_for_critique function to return a sample response
    sample_response = {
        "function": "sample_function",
        "error": "The docstring could be improved.",
        "warning": "The docstring could be improved.",
        "solution": '''
def sample_function(x, y):
    """
    Add two numbers together.

    This function takes two integers as input and returns their sum.

    Parameters
    ----------
    x : int
        The first number to add.
    y : int
        The second number to add.

    Returns
    -------
    int
        The sum of x and y.
    """
    return x + y
''',
    }

    with patch("docstring_auditor.main.ask_for_critique", return_value=sample_response):
        # read temp_file
        temp_file_contents = temp_file.read_text()
        assert "Subtract two numbers" in temp_file_contents

        # Call the docstring_auditor function with auto_fix=True
        runner = CliRunner()
        result = runner.invoke(docstring_auditor, ["--auto-fix", str(temp_file)])

        # read temp_file
        temp_file_contents = temp_file.read_text()
        # assert that the words "Add two numbers" is in the contents of temp_file
        assert "Add two numbers" in temp_file_contents
        # assert that the words "Subtract two numbers" is not in the contents of temp_file
        assert "Subtract two numbers" not in temp_file_contents


def test_docstring_auditor_update_middle_function(tmp_path):
    # Create a temporary Python file with three sample functions
    sample_code = '''
def function_one(x, y):
    """
    Add two numbers together.
    """
    return x + y

def function_two(x, y):
    """
    Subtract two numbers together.
    """
    return x - y

def function_three(x, y):
    """
    Multiply two numbers together.
    """
    return x * y
'''
    temp_file = tmp_path / "sample.py"
    temp_file.write_text(sample_code)

    # Mock the ask_for_critique function to return a sample response for function_two
    sample_response = {
        "function": "function_two",
        "error": "The docstring could be improved.",
        "warning": "The docstring could be improved.",
        "solution": '''
def function_two(x, y):
    """
    Subtract two numbers.

    This function takes two integers as input and returns the result of subtracting the second number from the first.

    Parameters
    ----------
    x : int
        The number to subtract from.
    y : int
        The number to subtract.

    Returns
    -------
    int
        The result of x - y.
    """
    return x - y
''',
    }

    with patch("docstring_auditor.main.ask_for_critique", return_value=sample_response):
        # read temp_file
        temp_file_contents = temp_file.read_text()
        assert "Subtract two numbers together." in temp_file_contents

        # Call the docstring_auditor function with auto_fix=True and code_block_name="function_two"
        runner = CliRunner()
        result = runner.invoke(
            docstring_auditor,
            ["--auto-fix", "--code-block-name", "function_two", str(temp_file)],
        )

        # read temp_file
        temp_file_contents = temp_file.read_text()
        # assert that the words "Subtract two numbers." is in the contents of temp_file
        assert "Subtract two numbers." in temp_file_contents
        # assert that the words "Subtract two numbers together." is not in the contents of temp_file
        assert "Subtract two numbers together." not in temp_file_contents
        # assert that the other functions' docstrings remain unchanged
        assert "Add two numbers together." in temp_file_contents
        assert "Multiply two numbers together." in temp_file_contents
