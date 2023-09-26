import sqlfluff

from .base import format_config, format_template
from .indent import replace_with_indentation


def format_sqlx(deconstructed_file: dict, dialect, config):
    """Formats Dataform SQLX files using SQLFluff"""
    # run fix on modified text
    bq_fix_result = sqlfluff.fix(
        deconstructed_file["main"], dialect=dialect, config_path=config
    )
    # place the templates back into the SQLX
    for mask, template in deconstructed_file["templates"].items():
        formatted_template = format_template(template)
        bq_fix_result = replace_with_indentation(
            bq_fix_result, mask, formatted_template
        )

    # recombine the config block and the fixed SQL
    formatted_config_block = format_config(deconstructed_file["config"])
    return formatted_config_block + "\n\n" + bq_fix_result
