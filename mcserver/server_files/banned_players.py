#Modules
# Standard
import json
import logging as log
from pathlib import Path
from typing import Literal, TypedDict

# MCServer
from minecraft.player_identity import normalize_player_uuid, PlayerID, PlayerUUID

#Paths
banned_players_file = Path("banned-players.json")

#TypedDicts
class BannedPlayerEntry(TypedDict):
    uuid: str
    name: str
    created: str                      # Time Format: yyyy-MM-dd HH:mm:ss Z
    source: str
    expires: str | Literal["forever"] # Time format: yyyy-MM-dd HH:mm:ss Z
    reason: str

class BannedPlayer(TypedDict):
    player_uuid: PlayerUUID
    player_name: str
    created_time: str                      # Time format: yyyy-MM-dd HH:mm:ss Z
    ban_source: str
    expires_time: str | Literal["forever"] # Time format: yyyy-MM-dd HH:mm:ss Z
    ban_reason: str

#Functions
# Add Players
def add_player(player_uuid: PlayerUUID, player_name: str, created_time: str, ban_source: str, expires_time: str | Literal["forever"] = "forever", ban_reason: str = "Banned via MCServer.") -> None:
    player_uuid = normalize_player_uuid(player_uuid)
    banned_player: BannedPlayer = {
        "player_uuid": player_uuid,
        "player_name": player_name,
        "created_time": created_time,
        "ban_source": ban_source,
        "expires_time": expires_time,
        "ban_reason": ban_reason
    }

    add_players(banned_player)

def add_players(banned_players: list[BannedPlayer] | BannedPlayer) -> None:
    if not isinstance(banned_players, list):
        banned_players = [banned_players]

    with open(banned_players_file, mode="r+") as file:
        banned_players_data = json.load(file)
        for player in banned_players:
            player_uuid = str(normalize_player_uuid(player["player_uuid"]))
            player_name = player["player_name"]
            ban_reason = player["ban_reason"]

            banned_player_entry: BannedPlayerEntry = {
                "uuid": player_uuid,
                "name": player_name,
                "created": player["created_time"],
                "source": player["ban_reason"],
                "expires": player["expires_time"],
                "reason": ban_reason
            }

            banned_players_data.append(banned_player_entry)
            log.debug(f"Added player '{player_name}' ({player_uuid}) to the banned player list with reason '{ban_reason}'")

        file.seek(0)
        json.dump(banned_players_data, file, indent=2)
        file.truncate()

# Remove Players
def remove_player(player_uuid: PlayerUUID | None = None, player_name: str | None = None) -> None:
    if player_uuid is None and player_name is None:
        raise ValueError("At least one of 'player_uuid' or 'player_name' must be provided")

    player_id: PlayerID = {}
    if player_uuid is not None:
        player_uuid = normalize_player_uuid(player_uuid)
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

    with open(banned_players_file, mode="r+") as file:
        banned_players_data: list[BannedPlayerEntry] = json.load(file)
        new_banned_players_data: list[BannedPlayerEntry] = []
        for player in banned_players_data:
            player_uuid = player["uuid"]
            player_name = player["name"]

            if player_uuid in player_uuids or player_name in player_names:
                log.debug(f"Removed player '{player_name}' ({player_uuid}) from the banned player list")
                continue

            new_banned_players_data.append(player)

        file.seek(0)
        json.dump(new_banned_players_data, file, indent=2)
        file.truncate()

# TODO: add 'update_player' and 'update_players', just use plain dict.update() because it has no depth

# List Players
def list_players() -> list[BannedPlayer]:
    banned_players_data: list[BannedPlayerEntry] = json.loads(banned_players_file.read_text())
    banned_players: list[BannedPlayer] = []
    for entry in banned_players_data:
        banned_player: BannedPlayer = {
            "player_uuid": entry["uuid"],
            "player_name": entry["name"],
            "created_time": entry["created"],
            "ban_source": entry["source"],
            "expires_time": entry["expires"],
            "ban_reason": entry["reason"]
        }

        banned_players.append(banned_player)

    return banned_players