import copy, json

import logging as log

from shared import mcserver_dir, merge_dict

# Variables
configs_dir = mcserver_dir / "configs"
default_configs = {
  "launcher": {
    "ram": {
      "_comment": "Memory size in MebiByte (MiB)",
      "min": 512,
      "max": 2_048
    },

    "jarfile": "Launcher.jar",
    "hide_gui": True
  },

  "modrinth": {
    "search_limit": 20,
    "sort_by": "relevance"
  },

  "server": {
    "version": "", # Auto-fetched the latest version when init without --mc-version
    "loader": {
      "name": "vanilla",
      "version": ""
    }
  }
}

# Functions
def generate_config(config_name: str, update_config: dict | None = None):
  if update_config is None: update_config = {}

  config_filename = f"{config_name}.json"
  config_path = configs_dir / config_filename

  try:
    config_content = copy.deepcopy(default_configs[config_name])
  except KeyError as error:
    raise ValueError(f"Failed to generate configuration file for '{config_name}': No default configuration available") from error

  config_data = merge_dict(config_content, update_config)

  try:
    with open(config_path, mode="xt") as config_file:
      json.dump(
        config_data,
        config_file,
        indent=2
      )
  except FileExistsError as error:
    raise FileExistsError(f"Cannot create configuration file for '{config_name}': File already exists") from error
  except FileNotFoundError as error:
    raise FileNotFoundError(f"Cannot create configuration file for '{config_name}': Configuration directory does not exist") from error
  except IsADirectoryError as error:
    raise IsADirectoryError(f"Cannot create configuration file for '{config_name}': Directory with same name already exists") from error
  except PermissionError as error:
    raise PermissionError(f"Cannot create configuration file for '{config_name}': Permission denied to create file") from error

def load_config(config_name: str, allow_missing: bool = False):
  config_filename = f"{config_name}.json"
  config_path = configs_dir / config_filename

  try:
    with open(config_path, mode="rt") as config_file:
      return json.load(config_file)
  except json.JSONDecodeError as error:
    msg = error.msg
    lineno = error.lineno
    colno = error.colno

    raise ValueError(f"Failed to load configuration for `{config_name}`: {msg} at line {lineno} column {colno}") from error

  except FileNotFoundError as error:
    if allow_missing:
      log.warning(f"Configuration file '{config_name}' is missing, using existing default value")

      try:
        return default_configs[config_name]
      except KeyError:
        raise KeyError(f"No default configuration found for '{config_name}'") from error # from the FileNotFoundError

    raise FileNotFoundError(f"Cannot read configuration file for '{config_name}': Configuration file does not exist") from error
  except IsADirectoryError as error:
    raise IsADirectoryError(f"Cannot read configuration file for '{config_name}': Not a file (is a directory)") from error
  except PermissionError as error:
    raise PermissionError(f"Cannot read configuration file for '{config_name}': Permission denied to read file") from error
