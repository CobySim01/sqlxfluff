import argparse
from sys import exit  # pylint: disable=redefined-builtin

import sqlfluff
from sqlfluff.core import FluffConfig
from termcolor import cprint

from .constants import EXIT_FAIL
from .formatters.javascript import validate_prettier_installation
from .formatters.sqlx import format_sqlx
from .linting import parse_sql, print_lint_result
from .parsing import parse_sqlx


def main():
    """Main entrypoint for the package."""

    validate_prettier_installation()

    parser = argparse.ArgumentParser(
        description="A script that formats and lints Dataform SQLX files."
    )
    parser.add_argument(
        "-c", "--config-path", help="Path to the configuration file", default=None
    )
    dialects = [d.name for d in sqlfluff.core.dialect_readout()]
    parser.add_argument(
        "-d", "--dialect", help="SQL dialect to use", choices=dialects, default=None
    )
    parser.add_argument(
        "files", metavar="FILE", type=str, nargs="+", help="File paths to process"
    )
    opts = parser.parse_args()

    for filename in opts.files:
        config = FluffConfig.from_path(
            filename if opts.config_path is None else opts.config_path
        )
        config.set_value(
            ["rules", "convention.terminator", "require_final_semicolon"], False
        )
        if opts.dialect is not None:
            config.set_value(["dialect"], opts.dialect)

        with open(filename, "r", encoding="utf-8") as f:
            raw_file_contents = f.read()
        parsed_file_contents = parse_sqlx(raw_file_contents)

        cprint(filename, attrs=["bold"], end=" ")

        parsing_violations = parse_sql(parsed_file_contents["main"], config)
        if parsing_violations is not None:
            cprint(parsing_violations, "red")
            exit(EXIT_FAIL)

        lint_result = sqlfluff.lint(parsed_file_contents["main"], config=config)
        if not lint_result:
            cprint("PASS", color="green")
        else:
            cprint("FAIL", color="red")
            for result in lint_result:
                print_lint_result(result)

        formatted_file_contents = format_sqlx(parsed_file_contents, config)
        formatted_file_contents_again = format_sqlx(
            parse_sqlx(formatted_file_contents), config
        )
        if formatted_file_contents != formatted_file_contents_again:
            cprint("Formatter unable to determine final formatted form.", "red")
            exit(EXIT_FAIL)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(formatted_file_contents)

        print()


if __name__ == "__main__":
    main()
