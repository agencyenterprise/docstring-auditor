from setuptools import setup, find_packages

setup(
    name="docstring-auditor",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "openai",
    ],
    entry_points={
        "console_scripts": [
            "docstring-auditor=docstring_auditor:main",
        ],
    },
    author="Rob Luke",
    author_email="code@robertluke.net",
    description="A tool to analyze Python functions' docstrings and provide critiques and suggestions for improvement",
    license="Apache License 2.0",
    keywords="docstring auditor openai gpt",
    url="https://github.com/rob-luke/docstring-auditor",
)