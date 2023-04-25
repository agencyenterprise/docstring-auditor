import pytest
from docstring_auditor.main import report_concerns
import click


def test_report_concerns_no_errors_no_warnings(monkeypatch):
    captured_output = []

    def mock_secho(*args, **kwargs):
        captured_output.append(args[0])

    monkeypatch.setattr(click, "secho", mock_secho)

    response_dict = {
        "function": "test_function",
        "error": "",
        "warning": "",
        "solution": "",
    }
    result = report_concerns(response_dict)
    assert result is False
    assert len(captured_output) == 1
    assert "No concerns found" in captured_output[0]


def test_report_concerns_error_only(monkeypatch):
    captured_output = []

    def mock_secho(*args, **kwargs):
        captured_output.append(args[0])

    monkeypatch.setattr(click, "secho", mock_secho)

    response_dict = {
        "function": "test_function",
        "error": "An error occurred.",
        "warning": "",
        "solution": "Updated docstring.",
    }
    result = report_concerns(response_dict)
    assert result is True
    assert len(captured_output) == 3
    assert "An error was found" in captured_output[0]
    assert "An error occurred." in captured_output[1]
    assert "Updated docstring.\n\n" in captured_output[2]


def test_report_concerns_warning_only(monkeypatch):
    captured_output = []

    def mock_secho(*args, **kwargs):
        captured_output.append(args[0])

    monkeypatch.setattr(click, "secho", mock_secho)

    response_dict = {
        "function": "test_function",
        "error": "",
        "warning": "A warning occurred.",
        "solution": "",
    }
    result = report_concerns(response_dict)
    assert result is True
    assert len(captured_output) == 2
    assert "A warning was found" in captured_output[0]
    assert "A warning occurred." in captured_output[1]


def test_report_concerns_error_and_warning(monkeypatch):
    captured_output = []

    def mock_secho(*args, **kwargs):
        captured_output.append(args[0])

    monkeypatch.setattr(click, "secho", mock_secho)

    response_dict = {
        "function": "test_function",
        "error": "An error occurred.",
        "warning": "A warning occurred.",
        "solution": "Updated docstring.",
    }
    result = report_concerns(response_dict)
    print(captured_output)
    assert result is True
    assert len(captured_output) == 5
    assert "An error was found" in captured_output[0]
    assert "An error occurred." in captured_output[1]
    assert "A warning was found" in captured_output[2]
    assert "A warning occurred." in captured_output[3]
    assert "Updated docstring.\n\n" in captured_output[4]
