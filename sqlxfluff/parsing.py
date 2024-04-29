import re
from uuid import uuid4 as uuid


def extract_block(file_contents, block_name):
    """Find a block (if one exists)."""
    block_open_match = re.search(block_name + r"\s+\{", file_contents)
    if block_name == "js":
        print(f"{block_open_match = }")
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
    # states
    OUTSIDE = 0
    INSIDE_DOLLAR = 1  # after we've seen a '$' character
    INSIDE_EXPR = 2

    state = OUTSIDE
    brace_count = 0
    expressions = []
    curr_expr = ""

    for char in text:
        if state == OUTSIDE:
            if char == "$":
                state = INSIDE_DOLLAR
                curr_expr += char
            continue

        if state == INSIDE_DOLLAR:
            if char == "{":
                brace_count += 1
                state = INSIDE_EXPR
                curr_expr += char
            else:
                state = OUTSIDE
                curr_expr = ""
            continue

        if state == INSIDE_EXPR:
            curr_expr += char
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    state = OUTSIDE
                    expressions.append(curr_expr)
                    curr_expr = ""

    # In case of unmatched braces, clear the current expression
    if brace_count != 0:
        curr_expr = ""

    return expressions


def parse_sqlx(file_contents: str):
    """Parses an SQLX file and splits into multiple components."""
    # split the text into a config block section and remaining text
    config_block_string = extract_block(file_contents, "config")
    js_block_string = extract_block(file_contents, "js")
    pre_operations_block_string = extract_block(file_contents, "pre_operations")
    post_operations_block_string = extract_block(file_contents, "post_operations")
    blocks_to_replace = [
        config_block_string,
        js_block_string,
        pre_operations_block_string,
        post_operations_block_string,
    ]
    remaining_text = file_contents
    for block in blocks_to_replace:
        remaining_text = remaining_text.replace(block, "").strip() + "\n"

    # Identify each template and replace it with a temporary mask
    templates = extract_templates(remaining_text)

    masks = {}
    for match in templates:
        # hacky way to generate a unique string that fits BigQuery's parsing rules
        # https://github.com/sqlfluff/sqlfluff/issues/1540#issuecomment-1110835283
        mask_string = "a" + str(uuid()).replace("-", ".a")
        remaining_text = remaining_text.replace(match, mask_string)
        masks[mask_string] = match

    return {
        "config": config_block_string,
        "js": js_block_string,
        "pre_operations": pre_operations_block_string,
        "post_operations": post_operations_block_string,
        "main": remaining_text,
        "templates": masks,
    }
