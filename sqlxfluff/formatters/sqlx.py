import sqlfluff

from .base import format_template, format_config
from termcolor import cprint
from sys import exit

from ..constants import EXIT_FAIL
from ..parsing import parse_sqlx


def format_sqlx(deconstructed_file: dict, dialect, config):
    """Formats Dataform SQLX files using SQLFluff"""
    # run fix on modified text
    bq_fix_result = sqlfluff.fix(
        deconstructed_file["main"], dialect=dialect, config_path=config
    )
    # place the templates back into the SQLX
    for mask, template in deconstructed_file["templates"].items():
        formatted_template = format_template(
            template["string"], indent_level=template["indent"]
        )
        bq_fix_result = bq_fix_result.replace(mask, formatted_template)

    # recombine the config block and the fixed SQL
    formatted_config_block = format_config(deconstructed_file["config"])
    return formatted_config_block + "\n\n" + bq_fix_result


def format_parsed_file(parsed_file: dict, dialect: str, config: str):
    """Formats the content of a file, raising an error if the
    formatter does not behave as expected."""
    # Assuming you have a Python function named 'format' that performs the actual formatting
    formatted_text = format_sqlx(parsed_file, dialect, config)

    new_parsed_file = parse_sqlx(formatted_text)

    if formatted_text != format_sqlx(new_parsed_file, dialect, config):
        print(formatted_text)
        print("***")
        print(format_sqlx(new_parsed_file, dialect, config))

        cprint("Formatter unable to determine final formatted form.", "red")
        exit(EXIT_FAIL)

    return formatted_text
