#Modules
# Standard
import json
from pathlib import Path
from typing import Literal, TypedDict
from uuid import UUID

# MCServer
from mcserver.minecraft.player_identity import normalize_player_uuid, PlayerID, PlayerUUID

#Paths
ops_file = Path("ops.json")

#TypedDicts
class OperatorEntry(TypedDict):
    uuid: str
    name: str
    level: Literal[0, 1, 2 ,3 ,4]
    bypassesPlayerLimit: bool

class OperatorPlayer(TypedDict):
    player_uuid: PlayerUUID
    player_name: str
    permission_level: Literal[0, 1 ,2 ,3 ,4]
    bypasses_player_limit: bool

#Functions
# Add Players
def add_player(player_uuid: PlayerUUID, player_name: str, permission_level: Literal[0, 1, 2, 3 ,4], bypasses_player_limit: bool = False) -> None:
    operator_player: OperatorPlayer = {
        "player_uuid": player_uuid,
        "player_name": player_name,
        "permission_level": permission_level,
        "bypasses_player_limit": bypasses_player_limit
    }

    add_players(operator_player)

def add_players(operator_players: list[OperatorPlayer] | OperatorPlayer) -> None:
    if not isinstance(operator_players, list):
        operator_players = [operator_players]

    with open(ops_file, mode="r+") as file:
        ops_data: list[OperatorEntry] = json.load(file)

        for player in operator_players:
            permission_level = player["permission_level"]
            if permission_level < 0 or permission_level > 4:
                raise ValueError("Permission level must be between 0 and 4.")

            operator_entry: OperatorEntry = {
                "uuid": str(normalize_player_uuid(player["player_uuid"])),
                "name": player["player_name"],
                "level": permission_level,
                "bypassesPlayerLimit": player["bypasses_player_limit"]
            }

            ops_data.append(operator_entry)

        file.seek(0)
        json.dump(ops_data, file, indent=2)
        file.truncate()

# Remove Players
def remove_player(player_uuid: PlayerUUID | None = None, player_name: str | None = None) -> None:
    if player_uuid is None and player_name is None:
        raise ValueError("At least one of 'player_uuid' or 'player_name' must be provided")

    player_id: PlayerID = {}
    if player_uuid is not None:
        player_id["player_uuid"] = normalize_player_uuid(player_uuid)
    
    if player_name is not None:
        player_id["player_name"] = player_name

    remove_players(player_id)

def remove_players(player_ids: list[PlayerID] | PlayerID) -> None:
    if not isinstance(player_ids, list):
        player_ids = [player_ids]

    player_uuids: set[PlayerUUID | None] = set()
    player_names: set[str | None] = set()

    for player_id in player_ids:
        if "player_uuid" in player_id:
            player_uuids.add(player_id["player_uuid"])

        if "player_name" in player_id:
            player_names.add(player_id["player_name"])

    with open(ops_file, mode="r+") as file:
        ops_data: list[OperatorEntry] = json.load(file)

        new_ops_data: list[OperatorEntry] = []
        for player in ops_data:
            if player["uuid"] in player_uuids or player["name"] in player_names:
                continue

            new_ops_data.append(player)

        file.seek(0)
        json.dump(new_ops_data, file, indent=2)
        file.truncate()

# TODO: add 'update_player' and 'update_players', just use plain dict.update() because it has no depth

# List Players
def list_players() -> list[OperatorPlayer]:
    ops_data: list[OperatorEntry] = json.loads(ops_file.read_text())
    operator_players: list[OperatorPlayer] = []
    for entry in ops_data:
        operator_player: OperatorPlayer = {
            "player_uuid": UUID(entry["uuid"]),
            "player_name": entry["name"],
            "permission_level": entry["level"],
            "bypasses_player_limit": entry["bypassesPlayerLimit"]
        }

        operator_players.append(operator_player)

    return operator_players
