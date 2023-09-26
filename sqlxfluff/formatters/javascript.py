import subprocess
from sys import exit  # pylint: disable=redefined-builtin

from termcolor import colored

from ..constants import EXIT_FAIL


def validate_prettier_installation():
    """Checks whether Prettier is installed, otherwise exits program."""
    try:
        subprocess.run(["prettier", "-v"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print(
            "Could not find Prettier installation. "
            f"Install using {colored('brew install prettier', 'green')}."
        )
        exit(EXIT_FAIL)


def format_with_prettier(js_code: str) -> str:
    """Formats a string of JavaScript code using Prettier."""
    cmd = ["prettier", "--stdin-filepath", "dummy-file.js", "--no-semi"]
    try:
        result = subprocess.run(
            cmd, input=js_code, text=True, capture_output=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("Error:", e.stderr)
        return js_code
