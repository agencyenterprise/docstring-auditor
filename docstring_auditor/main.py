#!/usr/bin/env python3

import os
import sys
import re
import click
import ast
import time
import json
from typing import List, Optional, Dict, Tuple
import openai


def extract_code_block(
    file_path: str, code_block_name: str = ""
) -> List[Optional[str]]:
    """
    Extract functions and methods from a Python file.

    This function reads a .py file and extracts each of the functions and methods from the
    file. It returns a list of strings, where each string contains the entire
    code for a function or method, including the definition, docstring, and code. If a specific
    code block name is provided, only that block will be extracted.

    Parameters
    ----------
    file_path: str
        The path to the .py file to extract functions and methods from.
    code_block_name: str, optional
        The name of a single block of code that you want audited, rather than all the code blocks.
        If you want all the code blocks audited, leave this blank. Defaults to ''.

    Returns
    -------
    List[Optional[str]]:
        A list of strings, where each string contains the entire code for a
        function or method, including the definition, docstring, and code.
    """
    with open(file_path, "r") as file:
        content = file.read()

    tree = ast.parse(content)
    functions_and_methods = []

    for func in tree.body:
        if isinstance(func, (ast.FunctionDef, ast.ClassDef)):
            if code_block_name == "" or func.name == code_block_name:
                functions_and_methods.append(ast.get_source_segment(content, func))

    for cls in [node for node in tree.body if isinstance(node, ast.ClassDef)]:
        for method in [node for node in cls.body if isinstance(node, ast.FunctionDef)]:
            if code_block_name == "" or method.name == code_block_name:
                functions_and_methods.append(ast.get_source_segment(content, method))

    return functions_and_methods


def ask_for_critique(function: str, model: str) -> Dict[str, str]:
    """
    Query OpenAI for a critique of the docstring for a function.

    Parameters
    ----------
    function : str
        A string containing the code and the docstring for the Python function.
        The input should be formatted as a single string, with the code and docstring combined.
    model : str
        The name of the OpenAI model to use for the query.

    Returns
    -------
    response_dict : Dict[str, str]
        A dictionary containing the analysis of the docstring, including function name, errors, warnings, and the corrected docstring if needed.
    """

    DESIRED_DOCSTRING_STYLE = "numpydoc"

    # Example taken from https://numpydoc.readthedocs.io/en/latest/example.html
    EXAMPLE_NUMPYDOC = r"""Summarize the function in one line.

    Several sentences providing an extended description. Refer to
    variables using back-ticks, e.g. `var`.

    Parameters
    ----------
    var1 : array_like
        Array_like means all those objects -- lists, nested lists, etc. --
        that can be converted to an array.  We can also refer to
        variables like `var1`.
    var2 : int
        The type above can either refer to an actual Python type
        (e.g. ``int``), or describe the type of the variable in more
        detail, e.g. ``(N,) ndarray`` or ``array_like``.
    *args : iterable
        Other arguments.
    long_var_name : {'hi', 'ho'}, optional
        Choices in brackets, default first when optional.

    Returns
    -------
    type
        Explanation of anonymous return value of type ``type``.
    describe : type
        Explanation of return value named `describe`.
    out : type
        Explanation of `out`.
    type_without_description

    Other Parameters
    ----------------
    only_seldom_used_keyword : int, optional
        Infrequently used parameters can be described under this optional
        section to prevent cluttering the Parameters section.
    **kwargs : dict
        Other infrequently used keyword arguments. Note that all keyword
        arguments appearing after the first parameter specified under the
        Other Parameters section, should also be described under this
        section.

    Raises
    ------
    BadException
        Because you shouldn't have done that.

    See Also
    --------
    numpy.array : Relationship (optional).
    numpy.ndarray : Relationship (optional), which could be fairly long, in
                    which case the line wraps here.
    numpy.dot, numpy.linalg.norm, numpy.eye

    Notes
    -----
    Notes about the implementation algorithm (if needed).

    This can have multiple paragraphs.

    You may include some math:

    .. math:: X(e^{j\omega } ) = x(n)e^{ - j\omega n}

    And even use a Greek symbol like :math:`\omega` inline.

    References
    ----------
    Cite the relevant literature, e.g. [1]_.  You may also cite these
    references in the notes section above.

    .. [1] O. McNoleg, "The integration of GIS, remote sensing,
       expert systems and adaptive co-kriging for environmental habitat
       modelling of the Highland Haggis using object-oriented, fuzzy-logic
       and neural-network techniques," Computers & Geosciences, vol. 22,
       pp. 585-588, 1996.

    Examples
    --------
    These are written in doctest format, and should illustrate how to
    use the function.

    >>> a = [1, 2, 3]
    >>> print([x + 3 for x in a])
    [4, 5, 6]
    >>> print("a\nb")
    a
    b
    """

    PROMPT_SYSTEM = (
        "You are a coding assistant. "
        "You are detail orientated and precise. "
        "You have extensive knowledge of all coding languages and packages. "
        "You will review the documentation for python functions that I provide. "
        "The documentation you are helping to write is written for someone with very little coding experience. "
        "Do not provide errors or warnings about imports. "
        "Please provide verbose descriptions and ensure no assumptions are made in the documentation. "
        "\n"
        "Here is an optimal example of a numpydoc string:\n"
        '\n'
        f"{EXAMPLE_NUMPYDOC}"
    )

    PROMPT_QUERY = (
        "In the next message, I will provide you with the code for a Python function. "
        f"This will include the docstrings, which should be in the {DESIRED_DOCSTRING_STYLE} style.\n\n"
        "Does the docstring for the function describe the functionality provided by the code? "
        "Does it exclude any functionality in the description? "
        "Would an extended summary help the user understand the function better? Be verbose. "
        "Is there adequate description of types and defaults? "
        "Not all aspects of the docstring are required (e.g. examples, references, see also, other parameters). But any included sections should be correct. "
        "Or does it document functionality that does not exist in the code?\n\n"
        "Do not provide errors or warnings about imports.\n\n"
        "Provide your response as JSON with the following format (do not return any additional text):\n"
        "{\n"
        '    "function": "Return the name of the function.",\n'
        '    "error": "Describe any errors in the docstring. For example, if any functionality is in the code but not in the docs. Or if any functionality is described in the docs, but does not exist in the code. If you find no errors, return an empty string.",\n'
        f'    "warning": "Describe any concerns, but not errors in the documentation. For example, possible typos, grammar errors, if the docstring does not follow the {DESIRED_DOCSTRING_STYLE} convention. If you find no warnings, return an empty string.",\n'
        '    "solution": "Place the corrected docstring here. Do not include modifications to the code, only include the improved docstring. Retain the triple quotes and indentation from the input data."\n'
        "}\n\n"
        "Example response:\n"
        "{\n"
        '    "function": "example_function",\n'
        '    "error": "The docstring excludes functionality related to the optional argument `y`. The docstring mentions a nonexistent `z` parameter.",\n'
        '    "warning": "The docstring does not follow the desired style and has a grammar error in the description.",\n'
        '    "solution": "def example_function(x, y=None):\\n\\n'
        '    """\\n'
        '    Compute the sum of x and y if y is provided, otherwise return x.\\n\\n'
        '    Parameters:\\n'
        '        x (int): The first number to be added.\\n'
        '        y (int, optional): The second number to be added. Defaults to None.\\n\\n'
        '    Returns:\\n'
        '        int: The sum of x and y, or x if y is not provided.\\n'
        '    """\\n"\n'
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
        model=model, temperature=0.0, messages=messages
    )

    response_str = response["choices"][0]["message"]["content"]
    response_dict = json.loads(response_str)

    return response_dict


def report_concerns(response_dict: Dict[str, str]) -> Tuple[int, int, str]:
    """
    Inform the user of any concerns with the docstring.

    Parameters
    ----------
    response_dict : Dict[str, str]
        A dictionary containing the function name, error, warning, and solution.

    Returns
    -------
    Tuple[int, int, str]
        Returns a tuple containing the count of errors and warnings found in the docstring, and the proposed solution.
    """
    function_name = response_dict["function"]
    error = response_dict["error"]
    warning = response_dict["warning"]
    solution = response_dict["solution"]

    error_count = 0
    warning_count = 0

    if not error and not warning:
        click.secho(
            f"No concerns found with the docstring for the function: {function_name}\n",
            fg="green",
        )
    else:
        if error:
            click.secho(
                f"An error was found in the function: {function_name}\n", fg="red"
            )
            click.secho(f"{error}\n", fg="red")
            error_count += 1
        if warning:
            click.secho(
                f"A warning was found in the function: {function_name}\n", fg="yellow"
            )
            click.secho(f"{warning}\n", fg="yellow")
            warning_count += 1
        if solution:
            click.secho(f"A proposed solution to these concerns is:\n\n{solution}\n\n")

    return error_count, warning_count, solution


def apply_solution(file_path: str, old_function: str, new_function: str):
    """Update the docstring of a function in a file.

    This function reads the content of a file, extracts the docstrings of the old_function and new_function,
    replaces the old docstring with the new docstring, and writes the updated content back to the file.

    Parameters
    ----------
    file_path : str
        The path to the file containing the function whose docstring needs to be updated.
    old_function : str
        The source code of the function with the old triple-quoted docstring.
    new_function : str
        The source code of the function with the new triple-quoted docstring.

    Returns
    -------
    None
        This function does not return any value. It modifies the file in-place.
    """
    with open(file_path, "r") as file:
        content = file.read()

    # Extract the old and new docstrings
    old_docstring = re.search(r'""".*?"""', old_function, flags=re.DOTALL).group(0)  # type: ignore
    if '"""' in new_function:
        new_docstring = re.search(r'""".*?"""', new_function, flags=re.DOTALL).group(0)  # type: ignore
    else:
        new_docstring = new_function

    # Replace the old docstring with the new docstring
    updated_content = content.replace(old_docstring, new_docstring)

    click.secho(f"Editing file: {file_path}", fg="red")
    with open(file_path, "w") as file:
        file.write(updated_content)


def process_file(
    file_path: str, model: str, auto_fix: bool, code_block_name: str = ""
) -> Tuple[int, int]:
    """
    Process a single Python file and analyze its functions' and methods' docstrings.

    This function processes the given Python file, extracts the functions and methods within it using the `extract_code_block` function,
    and analyzes their docstrings for errors and warnings using the `ask_for_critique` and `report_concerns` functions.
    It then returns the total number of errors and warnings found in the
    docstrings of the functions and methods in the given file.

    Parameters
    ----------
    file_path : str
        The path to the .py file to analyze the functions' and methods' docstrings.
    model : str
        The name of the OpenAI model to use for the analysis.
    auto_fix : bool
        Whether to automatically fix the errors and warnings found in the docstrings.
    code_block_name : str, optional
        The name of a single block of code that you want audited, rather than all the code blocks.
        If you want all the code blocks audited, leave this blank. Defaults to "".

    Returns
    -------
    Tuple[int, int]
        A tuple containing the total number of errors and warnings found in the docstrings of the functions and methods in the given file.
    """
    functions_and_methods = extract_code_block(file_path, code_block_name)

    error_count = 0
    warning_count = 0

    for idx, function_or_method in enumerate(functions_and_methods):
        print(
            f"Processing code {idx + 1} of {len(functions_and_methods)} in file {file_path}..."
        )
        assert isinstance(function_or_method, str)
        errors, warnings, solution = 0, 0, None
        for i in range(3):
            try:
                critique = ask_for_critique(function_or_method, model)
                errors, warnings, solution = report_concerns(critique)
                break
            except Exception as e:
                print(e)
                if i < 2:
                    print(f"Retrying in {2 ** i} seconds...")
                    time.sleep(2**i)
                else:
                    raise e
        error_count += errors
        warning_count += warnings

        if auto_fix and solution:
            apply_solution(file_path, function_or_method, solution)

    return error_count, warning_count


def process_directory(
    directory_path: str,
    model: str,
    auto_fix: bool,
    ignore_dirs: Optional[List[str]] = None,
    code_block_name: str = "",
) -> Tuple[int, int]:
    """
    Recursively process all .py files in a directory and its subdirectories, ignoring specified directories.

    Parameters
    ----------
    directory_path : str
        The path to the directory containing .py files to analyze the functions' docstrings.
    model : str
        The name of the OpenAI model to use for the docstring analysis.
    auto_fix : bool
        Whether to automatically fix the docstring errors and warnings.
    ignore_dirs : Optional[List[str]], optional
        A list of directory names to ignore while processing .py files. By default, it ignores the "tests" directory.
    code_block_name : str, optional
        The name of a single block of code that you want audited, rather than all the code blocks.
        If you want all the code blocks audited, leave this blank.

    Returns
    -------
    Tuple[int, int]
        A tuple containing the total number of errors and warnings found in the docstrings of the .py files.
    """
    if ignore_dirs is None:
        ignore_dirs = ["tests"]

    error_count = 0
    warning_count = 0

    for root, dirs, files in os.walk(directory_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                errors, warnings = process_file(
                    file_path, model, auto_fix, code_block_name
                )
                error_count += errors
                warning_count += warnings

    return error_count, warning_count


@click.command(name="DocstringAuditor")
@click.argument("path", type=click.Path(exists=True, readable=True), default=__file__)
@click.option(
    "--ignore-dirs",
    type=click.STRING,
    multiple=True,
    default=["tests"],
    help="A list of directory names to ignore while processing .py files. Separate multiple directories with a space.",
)
@click.option(
    "--error-on-warnings",
    is_flag=True,
    default=False,
    help="If true, warnings will be treated as errors and included in the exit code count.",
)
@click.option(
    "--model",
    type=click.STRING,
    default="gpt-4",
    help="The OpenAI model to use for docstring analysis. Default is 'gpt-4'.",
)
@click.option(
    "--code-block-name",
    type=click.STRING,
    default="",
    help="The name of a single block of code that you want audited, rather than all the code blocks.",
)
@click.option(
    "--auto-fix",
    is_flag=True,
    default=False,
    help="If true, the program will incorporate the suggested changes into the original file, overwriting the existing docstring.",
)
def docstring_auditor(
    path: str,
    ignore_dirs: List[str],
    error_on_warnings: bool,
    model: str,
    code_block_name: str,
    auto_fix: bool,
):
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
    error_on_warnings : bool
        If true, warnings will be treated as errors and included in the exit code count.
    model : str, optional
        The OpenAI model to use for docstring analysis. Default is 'gpt-4'.
    code_block_name : str, optional
        The name of a single block of code that you want audited, rather than all the code blocks.
        If you want all the code blocks audited, leave this blank. Default is an empty string.
    auto_fix : bool, optional
        If true, the program will incorporate the suggested changes into the original file, overwriting the existing docstring. Default is False. Suggestions are only applied if they are associated with an error, not a warning.

    Returns
    -------
    None
        The function does not return any value. It prints the critiques and suggestions for the docstrings in the given file or directory.
    """
    if os.path.isfile(path):
        error_count, warning_count = process_file(
            path, model, auto_fix, code_block_name
        )
    elif os.path.isdir(path):
        error_count, warning_count = process_directory(
            path, model, auto_fix, ignore_dirs, code_block_name
        )
    else:
        error_text = "Invalid path. Please provide a valid file or directory path."
        click.secho(error_text, fg="red")
        sys.exit(error_text)

    if error_count > 0 or (error_on_warnings and warning_count > 0):
        error_text = (
            f"Auditor identified {error_count} errors and {warning_count} warnings."
        )
        click.secho(error_text, fg="red")
        sys.exit(error_count + (warning_count if error_on_warnings else 0))
    else:
        click.secho("No errors found.", fg="green")
        sys.exit(0)


if __name__ == "__main__":
    docstring_auditor()
