#!/usr/bin/env python3

import os
import click
import ast
import json
from typing import List, Optional, Dict
import openai


def extract_functions(file_path: str) -> List[Optional[str]]:
    """
    Extract functions from a Python file.

    This function reads a .py file and extracts each of the functions from the
    file. It returns a list of strings, where each string contains the entire
    code for a function, including the definition, docstring, and code.

    Parameters
    ----------
    file_path : str
        The path to the .py file to extract functions from.

    Returns
    -------
    List[str]
        A list of strings, where each string contains the entire code for a
        function, including the definition, docstring, and code.

    Examples
    --------
    >>> file_path = 'path/to/your/python_file.py'
    >>> functions = extract_functions(file_path)
    >>> for function in functions:
    ...     print(function)
    ...     print('-' * 80)

    Notes
    -----
    This function may not work correctly for all cases, especially if there are
    nested functions or other complex structures.
    """
    with open(file_path, "r") as file:
        content = file.read()

    tree = ast.parse(content)
    functions = [
        ast.get_source_segment(content, func)
        for func in tree.body
        if isinstance(func, ast.FunctionDef)
    ]

    return functions


def ask_for_critique(function: str) -> Dict[str, str]:
    """
    Query OpenAI for a critique of the docstring for a function.

    Parameters
    ----------
    function : str
        A string containing the code and the docstring for the Python function.
        The input should be formatted as a single string, with the code and docstring combined.

    Returns
    -------
    response_dict : dict
        A dictionary containing the analysis of the docstring, including function name, errors, warnings, and the corrected docstring if needed.
    """

    DESIRED_DOCSTRING_STYLE = "numpydoc"

    PROMPT_SYSTEM = (
        "You are a coding assistant. "
        "You are detail orientated and precise. "
        "You have extensive knowledge of all coding languages and packages."
        "You will review the documentation for python functions that I provide."
        "The documentation you are helping to write is written for someone with very little coding experience."
        "Please provide verbose descriptions and ensure no assumptions are made in the documentation."
    )

    PROMPT_QUERY = (
        "In the next message, I will provide you with the code for a Python function. "
        f"This will include the docstrings, which should be in the {DESIRED_DOCSTRING_STYLE} style.\n\n"
        "Does the docstring for the function describe the functionality provided by the code? "
        "Does it exclude any functionality in the description? "
        "Would an extended summary help the user understand the function better? Be verbose. "
        "Is there adequate description of types and defaults? "
        "Or does it document functionality that does not exist in the code?\n\n"
        "Do not provide errors or warnings about imports.\n\n"
        "Provide your response as JSON with the following format (do not return any additional text):\n"
        "{\n"
        '    "function": "Return the name of the function.",\n'
        '    "error": "Describe any errors in the docstring. For example, if any functionality is in the code but not in the docs. Or if any functionality is described in the docs, but does not exist in the code. If you find no errors, return an empty string.",\n'
        f'    "warning": "Describe any concerns, but not errors in the documentation. For example, possible typos, grammar errors, if the docstring does not follow the {DESIRED_DOCSTRING_STYLE} convention. If you find no warnings, return an empty string.",\n'
        '    "solution": "If there were any errors, place the corrected docstring here. Do not include modifications to the code, only include the improved docstring"\n'
        "}"
    )

    messages = [
        {"role": "system", "content": PROMPT_SYSTEM},
        {"role": "user", "content": PROMPT_QUERY},
        {
            "role": "assistant",
            "content": "Please provide the code for the Python function and its docstring so I can analyze it for you.",
        },
        {"role": "user", "content": function},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4", temperature=0.1, messages=messages
    )

    response_str = response["choices"][0]["message"]["content"]
    response_dict = json.loads(response_str)

    return response_dict


def report_concerns(response_dict: Dict[str, str]) -> bool:
    """
    Inform the user of any concerns with the docstring.

    Parameters
    ----------
    response_dict : dict
        A dictionary containing the function name, error, warning, and solution.

    Returns
    -------
    bool
        Returns True if there are any concerns (errors or warnings), otherwise returns False.
    """
    function_name = response_dict["function"]
    error = response_dict["error"]
    warning = response_dict["warning"]
    solution = response_dict["solution"]

    if not error and not warning:
        click.secho(
            f"No concerns found with the docstring for the function: {function_name}\n",
            fg="green",
        )
        return False
    else:
        if error:
            click.secho(
                f"An error was found in the function: {function_name}\n", fg="red"
            )
            click.secho(f"{error}\n", fg="red")
        if warning:
            click.secho(
                f"A warning was found in the function: {function_name}\n", fg="yellow"
            )
            click.secho(f"{warning}\n", fg="yellow")
        if solution:
            click.secho(f"A proposed solution to these concerns is:\n\n{solution}\n\n")
        return True


def process_file(file_path: str):
    """
    Process a single Python file and analyze its functions' docstrings.

    Parameters
    ----------
    file_path : str
        The path to the .py file to analyze the functions' docstrings.

    Returns
    -------
    None
        The function does not return any value. It prints the critiques and suggestions for the docstrings in the given file.
    """
    functions = extract_functions(file_path)

    for idx, function in enumerate(functions):
        print(
            f"Processing function {idx + 1} of {len(functions)} in file {file_path}..."
        )
        assert isinstance(function, str)
        critique = ask_for_critique(function)
        report_concerns(critique)


def process_directory(directory_path: str, ignore_dirs: Optional[List[str]] = None):
    """
    Recursively process all .py files in a directory and its subdirectories, ignoring specified directories.

    Parameters
    ----------
    directory_path : str
        The path to the directory containing .py files to analyze the functions' docstrings.

    ignore_dirs : Optional[List[str]]
        A list of directory names to ignore while processing .py files. By default, it ignores the "tests" directory.

    Returns
    -------
    None
        The function does not return any value. It prints the critiques and suggestions for the docstrings in the .py files.
    """
    if ignore_dirs is None:
        ignore_dirs = ["tests"]

    for root, dirs, files in os.walk(directory_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                process_file(file_path)


@click.command(name="DocstringAuditor")
@click.argument("path", type=click.Path(exists=True, readable=True), default=__file__)
@click.option(
    "--ignore-dirs",
    type=click.STRING,
    multiple=True,
    default=["tests"],
    help="A list of directory names to ignore while processing .py files. Separate multiple directories with a space.",
)
def docstring_auditor(path: str, ignore_dirs: List[str]):
    """
    Analyze Python functions' docstrings in a given file or directory and provide critiques and suggestions for improvement.

    This program reads a Python file or directory, extracts the functions and their docstrings,
    and then analyzes the docstrings for errors, warnings,
    and possible improvements. The critiques and suggestions are then displayed to the user.

    Parameters
    ----------
    path : str
        The path to the .py file or directory to analyze the functions' docstrings.

    ignore_dirs : List[str]
        A list of directory names to ignore while processing .py files.

    Returns
    -------
    None
        The function does not return any value. It prints the critiques and suggestions for the docstrings in the given file or directory.
    """
    if os.path.isfile(path):
        process_file(path)
    elif os.path.isdir(path):
        process_directory(path, ignore_dirs)
    else:
        click.secho(
            "Invalid path. Please provide a valid file or directory path.", fg="red"
        )


if __name__ == "__main__":
    docstring_auditor()
