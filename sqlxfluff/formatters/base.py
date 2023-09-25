from jsbeautifier import default_options, beautify
import re


def format_javascript(string, options=None):
    """Formats JavaScript using JS Beautifier."""
    opts = default_options()
    opts.indent_size = 2
    opts.brace_style = "preserve-inline"
    if isinstance(options, dict):
        for key, value in options.items():
            setattr(opts, key, value)
    return beautify(string, opts=opts)


def format_template(string, indent_level=0):
    """Formats JavaScript templates from the code."""
    formatted_javascript = format_javascript(
        string.removeprefix("$").strip(), options={"indent_level": indent_level}
    )
    return re.sub(r"\{", "${", formatted_javascript, count=1)


def format_config(string):
    """Formats an SQLX config block."""
    return "config " + format_javascript(re.sub(r"config\s+\{", "{", string))
