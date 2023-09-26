import configparser
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


def recursive_convert_to_dict(config: configparser.ConfigParser):
    """Recursively converts a `ConfigParser` object to dictionary."""
    return {
        k: recursive_convert_to_dict(v) if not isinstance(v, str) else v
        for k, v in config.items()
    }


def load_config(path: str):
    """Loads a .sqlfluff config file as a dictionary"""
    config = configparser.ConfigParser()
    config.read(path)
    return recursive_convert_to_dict(config)
