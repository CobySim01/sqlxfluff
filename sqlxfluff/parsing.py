from uuid import uuid4 as uuid
import re


def extract_config_block(file_contents):
    """Find the config block (if one exists)."""
    config_block_open_match = re.search(r"config\s+\{", file_contents)
    if config_block_open_match is None:
        return ""
    config_block_open_start, config_block_open_end = config_block_open_match.span()
    num_open_brackets = 1
    num_chars_in_config_block = config_block_open_end - config_block_open_start
    for char in file_contents[config_block_open_end:]:
        if char == "{":
            num_open_brackets += 1
        elif char == "}":
            num_open_brackets -= 1
        num_chars_in_config_block += 1
        if num_open_brackets == 0:
            break
    return file_contents[
        config_block_open_start : config_block_open_start + num_chars_in_config_block
    ]


def extract_templates(text):
    """Extract's JavaScript templates from the code."""
    extracted = []
    stack = []
    temp_str = ""
    in_template = False
    current_indent = 0
    current_line_indent = 0
    non_space_seen = False  # whether non-space char has been seen in current line

    for char in text:
        # Reset the indentation count and non_space_seen flag at the start of a new line
        if char == "\n":
            current_line_indent = 0
            non_space_seen = False

        # Count the number of leading spaces/tabs to determine indentation
        elif char in (" ", "\t") and not in_template:
            current_line_indent += 1

        # Non-space, non-tab character
        elif char not in (" ", "\t", "\n"):
            non_space_seen = True  # Update the flag

        # Starting a template
        if char == "$" and not in_template:
            temp_str += char
            # Only set current_indent if no non-space characters have been seen yet on this line
            current_indent = 0 if non_space_seen else current_line_indent

        # Entering the template
        elif char == "{" and temp_str == "$":
            temp_str += char
            in_template = True
            stack.append("{")

        # Inside the template
        elif in_template:
            temp_str += char
            if char == "{":
                stack.append("{")
            elif char == "}":
                stack.pop()
                if not stack:
                    extracted.append({"string": temp_str, "indent": current_indent})
                    temp_str = ""
                    in_template = False
                    current_indent = 0

    return extracted


def parse_sqlx(file_contents: str):
    # split the text into a config block section and remaining text
    config_block_string = extract_config_block(file_contents)
    remaining_text = file_contents.replace(config_block_string, "")

    # Identify each template and replace it with a temporary mask
    templates = extract_templates(remaining_text)
    masks = {}
    for match in templates:
        # hacky way to generate a unique string that meets the BQ rules
        # https://github.com/sqlfluff/sqlfluff/issues/1540#issuecomment-1110835283
        mask_string = "a" + str(uuid()).replace("-", ".a")
        remaining_text = remaining_text.replace(match["string"], mask_string)
        masks[mask_string] = match

    return {
        "config": config_block_string,
        "main": remaining_text,
        "templates": masks,
    }
