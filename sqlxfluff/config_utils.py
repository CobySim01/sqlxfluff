from pathlib import Path, os

CONFIG_FILENAME = ".sqlfluff"


def find_config_file(path: str):
    """Find the relevant .sqlfluff config"""
    # Check the directory of the file
    path = Path(path)
    if (path / CONFIG_FILENAME).is_file():
        return str(path / CONFIG_FILENAME)
    # Check the parent directories
    if path.parent and path.parent != os.sep:
        return find_config_file(path.parent)
    # Return default
    return CONFIG_FILENAME
