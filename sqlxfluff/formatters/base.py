import re

from .indent import indent
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
