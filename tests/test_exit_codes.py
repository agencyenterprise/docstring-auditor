import pytest
import tempfile
from unittest.mock import patch
from docstring_auditor.main import docstring_auditor
from click.testing import CliRunner


# Test cases for sys exit values
test_data = [
    # (description, error_count, warning_count, error_on_warnings, expected_exit)
    ("No errors or warnings", 0, 0, False, 0),
    ("One error, no warnings", 1, 0, False, 1),
    ("No errors, one warning (no error on warnings)", 0, 1, False, 0),
    ("No errors, one warning (with error on warnings)", 0, 1, True, 1),
    ("One error, one warning (no error on warnings)", 1, 1, False, 1),
    ("One error, one warning (with error on warnings)", 1, 1, True, 2),
]


@pytest.mark.parametrize(
    "desc, error_count, warning_count, error_on_warnings, expected_exit", test_data
)
def test_docstring_auditor_exit_values(
    desc, error_count, warning_count, error_on_warnings, expected_exit
):
    with tempfile.TemporaryDirectory() as tempdir:
        with patch(
            "docstring_auditor.main.process_directory",
            return_value=(error_count, warning_count),
        ):
            runner = CliRunner()
            args = [tempdir, "--ignore-dirs", "tests"]
            if error_on_warnings:
                args.append("--error-on-warnings")
            result = runner.invoke(docstring_auditor, args=args)
            assert result.exit_code == expected_exit, f"{desc} failed"
