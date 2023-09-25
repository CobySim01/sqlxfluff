import argparse
from sys import exit  # pylint: disable=redefined-builtin


import sqlfluff

from termcolor import cprint

from .formatters.sqlx import format_parsed_file
from .config_utils import find_config_file
from .linting import parse_sql, print_lint_result
from .parsing import parse_sqlx
from .constants import EXIT_FAIL


def main():
    parser = argparse.ArgumentParser(
        description="A script that formats and lints Dataform SQLX files."
    )
    parser.add_argument(
        "-c", "--config", help="Path to the configuration file", default=None
    )
    dialects = [d.name for d in sqlfluff.core.dialect_readout()]
    parser.add_argument(
        "-d", "--dialect", help="SQL dialect to use", choices=dialects, default="ansi"
    )
    parser.add_argument(
        "files", metavar="FILE", type=str, nargs="+", help="File paths to process"
    )

    opts = parser.parse_args()

    for filename in opts.files:
        config_file = find_config_file(filename)
        with open(filename, "r", encoding="utf-8") as f:
            raw_file_contents = f.read()
        parsed_file_contents = parse_sqlx(raw_file_contents)

        parsing_violations = parse_sql(parsed_file_contents["main"], opts.dialect)
        if parsing_violations is not None:
            print(parsing_violations)
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

        formatted_file_contents = format_parsed_file(
            parsed_file_contents, opts.dialect, opts.config
        )
        with open(filename, "w", encoding="utf-8") as f:
            f.write(formatted_file_contents)


if __name__ == "__main__":
    main()
