import pytest
from docstring_auditor.main import ask_for_critique
from unittest.mock import MagicMock
import openai


def mock_chatcompletion_create(*args, **kwargs):
    response = {
        "choices": [
            {
                "message": {
                    "content": (
                        "{"
                        '  "function": "test_function",'
                        '  "error": "An error occurred.",'
                        '  "warning": "A warning occurred.",'
                        '  "solution": "Updated docstring."'
                        "}"
                    )
                }
            }
        ]
    }
    return response


@pytest.fixture(autouse=True)
def openai_mock(monkeypatch):
    monkeypatch.setattr(openai.ChatCompletion, "create", mock_chatcompletion_create)


def test_ask_for_critique():
    function = (
        "def test_function():\n"
        '    """This is a test function."""\n'
        "    return 'successful'\n"
    )

    response_dict = ask_for_critique(function)
    assert response_dict["function"] == "test_function"
    assert response_dict["error"] == "An error occurred."
    assert response_dict["warning"] == "A warning occurred."
    assert response_dict["solution"] == "Updated docstring."


def mock_chatcompletion_create_no_errors_warnings(*args, **kwargs):
    response = {
        "choices": [
            {
                "message": {
                    "content": (
                        "{"
                        '  "function": "test_function_no_errors_warnings",'
                        '  "error": "",'
                        '  "warning": "",'
                        '  "solution": ""'
                        "}"
                    )
                }
            }
        ]
    }
    return response


def mock_chatcompletion_create_only_warning(*args, **kwargs):
    response = {
        "choices": [
            {
                "message": {
                    "content": (
                        "{"
                        '  "function": "test_function_only_warning",'
                        '  "error": "",'
                        '  "warning": "A warning occurred.",'
                        '  "solution": ""'
                        "}"
                    )
                }
            }
        ]
    }
    return response


def mock_chatcompletion_create_only_error(*args, **kwargs):
    response = {
        "choices": [
            {
                "message": {
                    "content": (
                        "{"
                        '  "function": "test_function_only_error",'
                        '  "error": "An error occurred.",'
                        '  "warning": "",'
                        '  "solution": "Updated docstring."'
                        "}"
                    )
                }
            }
        ]
    }
    return response


def mock_chatcompletion_create_error_and_solution(*args, **kwargs):
    response = {
        "choices": [
            {
                "message": {
                    "content": (
                        "{"
                        '  "function": "test_function_error_and_solution",'
                        '  "error": "An error occurred.",'
                        '  "warning": "",'
                        '  "solution": "Updated docstring."'
                        "}"
                    )
                }
            }
        ]
    }
    return response


def mock_chatcompletion_create_warning_and_solution(*args, **kwargs):
    response = {
        "choices": [
            {
                "message": {
                    "content": (
                        "{"
                        '  "function": "test_function_warning_and_solution",'
                        '  "error": "",'
                        '  "warning": "A warning occurred.",'
                        '  "solution": "Updated docstring."'
                        "}"
                    )
                }
            }
        ]
    }
    return response


@pytest.fixture(
    params=[
        mock_chatcompletion_create_no_errors_warnings,
        mock_chatcompletion_create_only_warning,
        mock_chatcompletion_create_only_error,
        mock_chatcompletion_create_error_and_solution,
        mock_chatcompletion_create_warning_and_solution,
    ],
    ids=[
        "no_errors_warnings",
        "only_warning",
        "only_error",
        "error_and_solution",
        "warning_and_solution",
    ],
)
def openai_mock(monkeypatch, request):
    monkeypatch.setattr(openai.ChatCompletion, "create", request.param)
    return request  # Return the request object


def test_ask_for_critique(openai_mock):
    function = (
        "def test_function():\n"
        '    """This is a test function."""\n'
        "    return 'successful'\n"
    )

    response_dict = ask_for_critique(function)
    assert response_dict["function"].startswith("test_function_")

    current_test_id = (
        openai_mock.param.__name__
    )  # Access the current mock function's name
    if "no_errors_warnings" in current_test_id:
        assert response_dict["error"] == ""
        assert response_dict["warning"] == ""
        assert response_dict["solution"] == ""
    elif "only_warning" in current_test_id:
        assert response_dict["error"] == ""
        assert response_dict["warning"] == "A warning occurred."
        assert response_dict["solution"] == ""
    elif "only_error" in current_test_id:
        assert response_dict["error"] == "An error occurred."
        assert response_dict["warning"] == ""
        assert response_dict["solution"] == "Updated docstring."
    elif "error_and_solution" in current_test_id:
        assert response_dict["error"] == "An error occurred."
        assert response_dict["warning"] == ""
        assert response_dict["solution"] == "Updated docstring."
    elif "warning_and_solution" in current_test_id:
        assert response_dict["error"] == ""
        assert response_dict["warning"] == "A warning occurred."
        assert response_dict["solution"] == "Updated docstring."
