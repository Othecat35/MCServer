from types import new_class
import json, uuid
from pathlib import Path

whitelist_file = Path("whitelist.json")

def add_player(player_uuid: str, player_name: str) -> None:
    player_uuid = str(uuid.UUID(player_uuid))
    with open(whitelist_file, mode="r+") as file:
        whitelist_data = json.load(file)
        whitelist_data.append({
            "uuid": player_uuid,
            "name": player_name
        })

        json.dump(whitelist_data, file, indent=2)

# TODO: Complete this function
# def list_players() -> list[WhitelistedPlayerIdentity]:
#     pass

def remove_player(player_uuid: str) -> None:
    player_uuid = str(uuid.UUID(player_uuid))
    with open(whitelist_file, mode="r+") as file:
        whitelist_data = json.load(file)

        new_data = []
        for player in whitelist_data:
            if player["uuid"] == player_uuid:
                continue

            new_data.append(player)

        json.dump(new_data, file, indent=2)