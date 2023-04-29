import pytest
from docstring_auditor.main import extract_code_block
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
    functions = extract_code_block(file_path)
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
    functions = extract_code_block(file_path)
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
    functions = extract_code_block(file_path)
    assert len(functions) == 3
    assert "def test_function():" in functions[1]


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
    functions = extract_code_block(file_path)
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
    functions = extract_code_block(file_path)
    assert len(functions) == 1


def test_extract_functions_class_with_methods(cleanup):
    content = """
class TestClass:
    def method1(self):
        return "method1"

    def method2(self):
        return "method2"
"""

    file_path = create_temp_file(content)
    functions = extract_code_block(file_path)
    assert len(functions) == 3
    assert "class TestClass:" in functions[0]
    assert "def method1(self):" in functions[1]
    assert "def method2(self):" in functions[2]


def test_extract_functions_class_with_static_methods(cleanup):
    content = """
class TestClass:
    @staticmethod
    def static_method():
        return "static_method"
"""

    file_path = create_temp_file(content)
    functions = extract_code_block(file_path)
    assert len(functions) == 2
    assert "class TestClass:" in functions[0]
    assert "def static_method():" in functions[1]


def test_extract_functions_class_with_class_methods(cleanup):
    content = """
class TestClass:
    @classmethod
    def class_method(cls):
        return "class_method"
"""

    file_path = create_temp_file(content)
    functions = extract_code_block(file_path)
    assert len(functions) == 2
    assert "class TestClass:" in functions[0]
    assert "def class_method(cls):" in functions[1]


def test_extract_functions_class_with_property_methods(cleanup):
    content = """
class TestClass:
    @property
    def property_method(self):
        return "property_method"
"""

    file_path = create_temp_file(content)
    functions = extract_code_block(file_path)
    assert len(functions) == 2
    assert "class TestClass:" in functions[0]
    assert "def property_method(self):" in functions[1]


def test_extract_functions_class_with_setter_methods(cleanup):
    content = """
class TestClass:
    @property
    def property_method(self):
        return "property_method"

    @property_method.setter
    def property_method(self, value):
        pass
"""

    file_path = create_temp_file(content)
    functions = extract_code_block(file_path)
    assert len(functions) == 3
    assert "class TestClass:" in "".join(functions)
    assert "def property_method(self):" in "".join(functions)
    assert "def property_method(self, value):" in "".join(functions)


def test_extract_functions_class_with_inheritance(cleanup):
    content = """
class ParentClass:
    def parent_method(self):
        return "parent_method"

class ChildClass(ParentClass):
    def child_method(self):
        return "child_method"
"""

    file_path = create_temp_file(content)
    functions = extract_code_block(file_path)
    assert len(functions) == 4
    assert "class ParentClass:" in "".join(functions)
    assert "def parent_method(self):" in "".join(functions)
    assert "class ChildClass(ParentClass):" in "".join(functions)
    assert "def child_method(self):" in "".join(functions)


def test_extract_functions_class_with_multiple_inheritance(cleanup):
    content = """
class ParentClass1:
    def parent_method1(self):
        return "parent_method1"

class ParentClass2:
    def parent_method2(self):
        return "parent_method2"

class ChildClass(ParentClass1, ParentClass2):
    def child_method(self):
        return "child_method"
"""

    file_path = create_temp_file(content)
    functions = extract_code_block(file_path)
    assert len(functions) == 6
    assert "class ParentClass1:" in "".join(functions)
    assert "def parent_method1(self):" in "".join(functions)
    assert "class ParentClass2:" in "".join(functions)
    assert "def parent_method2(self):" in "".join(functions)
    assert "class ChildClass(ParentClass1, ParentClass2):" in "".join(functions)
    assert "def child_method(self):" in "".join(functions)


def test_extract_code_block_single_function_by_name(cleanup):
    content = """
def test_function1():
    return "successful"

def test_function2():
    return "successful"
"""

    file_path = create_temp_file(content)
    functions = extract_code_block(file_path, code_block_name="test_function1")
    assert len(functions) == 1
    assert "def test_function1():" in functions[0]


def test_extract_code_block_class_method_by_name(cleanup):
    content = """
class TestClass:
    def method1(self):
        return "method1"

    def method2(self):
        return "method2"
"""

    file_path = create_temp_file(content)
    functions = extract_code_block(file_path, code_block_name="method1")
    assert len(functions) == 1
    assert "def method1(self):" in functions[0]


def test_extract_code_block_class_by_name(cleanup):
    content = """
class TestClass1:
    def method1(self):
        return "method1"

class TestClass2:
    def method2(self):
        return "method2"
"""

    file_path = create_temp_file(content)
    functions = extract_code_block(file_path, code_block_name="TestClass1")
    assert len(functions) == 1
    assert "class TestClass1:" in functions[0]


def test_extract_code_block_no_matching_name(cleanup):
    content = """
def test_function1():
    return "successful"

def test_function2():
    return "successful"
"""

    file_path = create_temp_file(content)
    functions = extract_code_block(file_path, code_block_name="non_existent_function")
    assert len(functions) == 0
