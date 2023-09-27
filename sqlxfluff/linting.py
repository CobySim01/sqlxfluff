import sqlfluff
from sqlfluff.api import APIParsingError
from termcolor import colored


def parse_sql(sql_string: str, config):
    """Returns whether or not the provided SQL is parseable by SQLFluff."""
    try:
        sqlfluff.parse(sql_string, config=config)
    except APIParsingError as error:
        return error.msg
    return None


def print_lint_result(result):
    """Prints a result from `sqlfluff.lint`."""
    line_no = result.get("line_no", "")
    line_pos = result.get("line_pos", "")
    code = result.get("code", "")
    description = result.get("description", "")
    name = result.get("name", "")

    # Formatting the table row
    print(colored(f"L:{line_no:4} | P:{line_pos:4} | {code:4} |", "blue"), description)
    bold_name = colored(name, attrs=["bold"])
    print(" " * 23 + colored("|", "blue"), f"[{bold_name}]")
