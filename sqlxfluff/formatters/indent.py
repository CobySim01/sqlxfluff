import re


def indent(string_or_lists: str | list[str], indent_level: int):
    """Indents each line of `string` by `indent_level` spaces."""
    if isinstance(string_or_lists, str):
        lst = string_or_lists.split("\n")
    else:
        lst = string_or_lists
    spaces = " " * indent_level
    return "\n".join(spaces + line if line.strip() else line for line in lst)


def replace_with_indentation(source, target, replacement):
    """Replace `target` in `source` with `replacement`, while maintaining the
    indentation level of `target`"""
    # Find target in source
    match = re.search(re.escape(target), source)

    if not match:
        return source

    # Determine the start of the line where the target string was found
    line_start = source.rfind("\n", 0, match.start()) + 1

    # Compute the indentation as the spaces from the start of the line until the first non-space character
    indentation_level = 0
    for char in source[line_start : match.start()]:
        if char != " ":
            break
        indentation_level += 1

    # Split replacement into lines
    replacement_lines = replacement.split("\n")

    # If the target is not the start of its line, don't indent the first line of the replacement
    if source[line_start : match.start()].strip():
        indented_replacement = replacement_lines[0] + "\n"
        indented_replacement += indent(replacement_lines[1:], indentation_level)
    else:
        indented_replacement = indent(replacement_lines, indentation_level)

    # Replace target with indented replacement in source
    return source.replace(match.group(0), indented_replacement.strip())
