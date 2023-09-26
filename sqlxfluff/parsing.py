import re
from uuid import uuid4 as uuid


def extract_block(file_contents, block_name):
    """Find a block (if one exists)."""
    block_open_match = re.search(block_name + r"\s+\{", file_contents)
    if block_open_match is None:
        return ""
    block_open_start, block_open_end = block_open_match.span()
    num_open_brackets = 1
    num_chars_in_block = block_open_end - block_open_start
    for char in file_contents[block_open_end:]:
        if char == "{":
            num_open_brackets += 1
        elif char == "}":
            num_open_brackets -= 1
        num_chars_in_block += 1
        if num_open_brackets == 0:
            break
    return file_contents[block_open_start : block_open_start + num_chars_in_block]


def extract_templates(text):
    """Extract's JavaScript templates from string."""
    extracted = []
    stack = []
    temp_str = ""
    in_template = False

    for char in text:
        # Starting a template
        if char == "$" and not in_template:
            temp_str += char

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
                    extracted.append(temp_str)
                    temp_str = ""
                    in_template = False

    return extracted


def parse_sqlx(file_contents: str):
    """Parses an SQLX file and splits into multiple components."""
    # split the text into a config block section and remaining text
    config_block_string = extract_block(file_contents, "config")
    js_block_string = extract_block(file_contents, "js")
    remaining_text = (
        file_contents.replace(config_block_string, "")
        .replace(js_block_string, "")
        .strip()
        + "\n"
    )

    # Identify each template and replace it with a temporary mask
    templates = extract_templates(remaining_text)

    masks = {}
    for match in templates:
        # hacky way to generate a unique string that meets the BQ rules
        # https://github.com/sqlfluff/sqlfluff/issues/1540#issuecomment-1110835283
        mask_string = "a" + str(uuid()).replace("-", ".a")
        remaining_text = remaining_text.replace(match, mask_string)
        masks[mask_string] = match

    return {
        "config": config_block_string,
        "js": js_block_string,
        "main": remaining_text,
        "templates": masks,
    }
