import pytest
from docstring_auditor.main import extract_functions
import os


def create_temp_file(content):
    with open("temp.py", "w") as f:
        f.write(content)
    return "temp.py"


@pytest.fixture
def cleanup():
    yield
    if os.path.exists("temp.py"):
        os.remove("temp.py")


def test_extract_functions_single_function(cleanup):
    content = """
def test_function():
    return "successful"
"""
    file_path = create_temp_file(content)
    functions = extract_functions(file_path)
    assert len(functions) == 1
    assert "def test_function():" in functions[0]


def test_extract_functions_multiple_functions(cleanup):
    content = """
def test_function1():
    return "successful"

def test_function2():
    return "successful"
"""

    file_path = create_temp_file(content)
    functions = extract_functions(file_path)
    assert len(functions) == 2
    assert "def test_function1():" in functions[0]
    assert "def test_function2():" in functions[1]


def test_extract_functions_with_class(cleanup):
    content = """
class TestClass:
    def test_function_class(self):
        return "successful"

def test_function():
    return "successful"
"""

    file_path = create_temp_file(content)
    functions = extract_functions(file_path)
    assert len(functions) == 1
    assert "def test_function():" in functions[0]


def test_extract_functions_nested_functions(cleanup):
    content = """
def outer_function():
    def inner_function():
        return "successful"
    return inner_function()

def normal_function():
    return "successful"
"""

    file_path = create_temp_file(content)
    functions = extract_functions(file_path)
    assert len(functions) == 2
    assert "def outer_function():" in functions[0]
    assert "def normal_function():" in functions[1]


def test_extract_functions_no_functions(cleanup):
    content = """
class NoFunctionClass:
    pass

variable = "some_value"
"""

    file_path = create_temp_file(content)
    functions = extract_functions(file_path)
    assert len(functions) == 0
