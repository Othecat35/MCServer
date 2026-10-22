# Modules
# Standard
import json
from typing import Any

# MCServer
from .paths import configs_dir


class ConfigVersionError(Exception):
    pass


# Functions
def write_config(
    config_name: str, format_version: int, config_data: dict[str, Any]
) -> None:
    """Write the configuration data to a file

    Args:
        config_name: The name of the configuration
        format_version: The format version of this configuration data
        config_data: The configuration data

    Raises:
        FileNotFoundError: The configuration directory does not exist
    """
    if not configs_dir.exists():
        raise FileNotFoundError(
            f"COnfiguration directory '{configs_dir}' does not exist"
        )

    config_filename = f"{config_name}.json"
    config_path = configs_dir / config_filename
    config_data["format_version"] = format_version

    config_json = json.dumps(config_data)
    config_path.write_text(config_json)


def read_config(config_name: str, current_format_version: int) -> dict[str, Any]:
    """Read a configuration file

    Args:
        config_name: The name of the configuration
        current_format_version: The current format version for the configuration

    Raises:
        FileNotFoundError: The configuration file does not exist
    """

    config_filename = f"{config_name}.json"
    config_path = configs_dir / config_filename

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file for '{config_name}' does not exist"
        )

    config_json = config_path.read_text()
    config_data = json.loads(config_json)

    if config_data["format_version"] > current_format_version:
        raise ConfigVersionError("")

    return config_data
