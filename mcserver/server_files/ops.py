#Modules
# Standard
import json
from pathlib import Path
from typing import TypedDict
from uuid import UUID

# MCServer
from minecraft.player_identity import normalize_player_uuid, PlayerID, PlayerUUID

#Paths
ops_file = Path("ops.json")

#TypedDicts
class OpsEntry(TypedDict):
    uuid: str
    name: str
    level: int
    bypassesPlayerLimit: bool

class OperatorPlayer(TypedDict):
    player_uuid: PlayerUUID
    player_name: str
    permission_level: int
    bypasses_player_limit: bool

#Functions
def add_player(player_uuid: PlayerUUID, player_name: str, permission_level: int, bypasses_player_limit: bool = False) -> None:
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
        ops_data: list[OpsEntry] = json.load(file)

        for player in operator_players:
            ops_data.append({
                "uuid": str(normalize_player_uuid(player["player_uuid"])),
                "name": player["player_name"],
                "level": player["permission_level"],
                "bypassesPlayerLimit": player["bypasses_player_limit"]
            })

        file.seek(0)
        json.dump(ops_data, file, indent=2)
        file.truncate()

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
        ops_data: list[OpsEntry] = json.load(file)

        new_ops_data: list[OpsEntry] = []
        for player in ops_data:
            if player["uuid"] in player_uuids or player["name"] in player_names:
                continue

            new_ops_data.append(player)

        file.seek(0)
        json.dump(new_ops_data, file, indent=2)
        file.truncate()

# TODO: add 'update_player' and 'update_players', just use plain dict.update() because it has no depth

def list_players() -> list[OperatorPlayer]:
    ops_data: list[OpsEntry] = json.loads(ops_file.read_text())

    operator_players: list[OperatorPlayer] = []
    for player in ops_data:
        operator_players.append({
            "player_uuid": UUID(player["uuid"]),
            "player_name": player["name"],
            "permission_level": player["level"],
            "bypasses_player_limit": player["bypassesPlayerLimit"]
        })

    return operator_players
