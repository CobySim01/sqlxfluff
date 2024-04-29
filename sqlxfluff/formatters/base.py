import re

from .indent import deindent, indent
from .javascript import format_with_prettier


def format_template(string):
    """Formats JavaScript templates from the code."""
    formatted_javascript = format_with_prettier(
        string.removeprefix("${").removesuffix("}").strip()
    )
    if "\n" in formatted_javascript:
        return "${\n" + indent(formatted_javascript, 2) + "\n}"
    return "${ " + formatted_javascript.strip() + " }"


def format_config(string):
    """Formats an SQLX config block."""
    MOCK_VARIABLE_NAME = "var configMockVariable = "
    mock_javascript = re.sub(r"config\s+\{", MOCK_VARIABLE_NAME + "{", string)
    return "config " + format_with_prettier(mock_javascript).removeprefix(
        MOCK_VARIABLE_NAME
    )


def format_js(string):
    """Formats a js block."""
    mock_javascript = re.sub(
        r"}\s*$", "", re.sub(r"^\s*js\s+{", "", string, count=1), count=1
    )
    formatted_javascript_with_indent = indent(
        format_with_prettier(deindent(mock_javascript, 2)), 2
    )
    return "js {\n" + formatted_javascript_with_indent + "\n}"
