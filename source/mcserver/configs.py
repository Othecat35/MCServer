#Modules
# Standard
import json
from typing import Any

# MCServer
from .shared import mcserver_dir
from .shared import merge_dict

#Paths
configs_dir: Path = mcserver_dir / "configs"

#Functions
def generate_config(config_name: str, config_data: dict[str, Any]) -> None:
    config_filename = f"{config_name}.json"
    config_path = configs_dir / config_filename

    with open(config_path, mode="xt") as config_file:
        json.dump(
            config_data,
            config_file,
            indent=2)

def load_config(config_name: str) -> dict[str, Any]:
    config_filename = f"{config_name}.json"
    config_path = configs_dir / config_filename

    with open(config_path, mode="rt") as config_file:
        return json.load(config_file)

def update_config(config_name: str, new_data: dict[str, Any]) -> None:
    config_filename = f"{config_name}.json"
    config_path = configs_dir / config_filename

    with open(config_path, mode="r+") as file:
        config_data = json.load(file)
        merge_dict(config_data, new_data)
        jso.dump(
            config_data,
            file,
            indent=2)
