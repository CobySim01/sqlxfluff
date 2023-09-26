import argparse
from sys import exit  # pylint: disable=redefined-builtin

import sqlfluff
from termcolor import cprint

from .config_utils import find_config_file, load_config
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
        "-c", "--config", help="Path to the configuration file", default=None
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
        if opts.config is None:
            opts.config = find_config_file(filename)
        if opts.dialect is None:
            opts.dialect = load_config(opts.config).get("sqlfluff", {}).get("dialect")

        with open(filename, "r", encoding="utf-8") as f:
            raw_file_contents = f.read()
        parsed_file_contents = parse_sqlx(raw_file_contents)

        parsing_violations = parse_sql(parsed_file_contents["main"], opts.dialect)
        if parsing_violations is not None:
            cprint(parsing_violations, "red")
            exit(EXIT_FAIL)

        lint_result = sqlfluff.lint(
            parsed_file_contents["main"],
            dialect=opts.dialect,
            config_path=opts.config,
        )
        cprint(filename, attrs=["bold"], end=" ")
        if not lint_result:
            cprint("PASS", color="green")
        else:
            cprint("FAIL", color="red")
            for result in lint_result:
                print_lint_result(result)

        formatted_file_contents = format_sqlx(
            parsed_file_contents, opts.dialect, opts.config
        )
        formatted_file_contents_again = format_sqlx(
            parse_sqlx(formatted_file_contents), opts.dialect, opts.config
        )
        if formatted_file_contents != formatted_file_contents_again:
            cprint("Formatter unable to determine final formatted form.", "red")
            exit(EXIT_FAIL)

        with open(filename, "w", encoding="utf-8") as f:
            f.write(formatted_file_contents)

        print()


if __name__ == "__main__":
    main()
