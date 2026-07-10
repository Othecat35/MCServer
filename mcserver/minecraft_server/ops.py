import json, uuid
from pathlib import Path
from typing import TypedDict

ops_file = Path("ops.json")

def add_player(player_uuid: str, player_name: str, permission_level_number: int, can_bypass_player_limit: bool) -> None:
    with open(ops_file, mode="rwt") as file:
        data_json = json.load(file)
        data_json.append({
            "uuid": uuid.UUID(player_uuid),
            "name": player_name,
            "level": permission_level,
            "bypassPlayerLimit": bypass_player_limit
        })

        json.dump(data, file, indent=2)

def remove_player(player_uuid: str)