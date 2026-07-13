#Modules
# Standard
import json
import logging as log
from pathlib import Path
from typing import TypedDict
from uuid import UUID

# MCServer
from minecraft.player_identity import normalize_player_uuid, PlayerID, PlayerUUID

#Paths
whitelisted_file = Path("whitelisted.json")

#TypedDicts
class WhitelistedEntry(TypedDict):
    uuid: str
    name: str

class WhitelistedPlayer(TypedDict):
    player_uuid: PlayerUUID
    player_name: str

#Functions
# Add Playersa
def add_player(player_uuid: PlayerUUID, player_name: str) -> None:
    whitelisted_player: WhitelistedPlayer = {
        "player_uuid": player_uuid,
        "player_name": player_name
    }

    add_players(whitelisted_player)

def add_players(whitelisted_players: list[WhitelistedPlayer] | WhitelistedPlayer) -> None:
    if not isinstance(whitelisted_players, list):
        whitelisted_players = [whitelisted_players]

    with open(whitelisted_file, mode="r+") as file:
        whitelisted_data = json.load(file)

        for player in whitelisted_players:
            whitelisted_entry: WhitelistedEntry = {
                "uuid": str(normalize_player_uuid(player["player_uuid"])),
                "name": player["player_name"]
            }

            whitelisted_data.append(whitelisted_entry)

        file.seek(0)
        json.dump(whitelisted_data, file, indent=2)
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

    with open(whitelisted_file, mode="r+") as file:
        whitelisted_data: list[WhitelistedEntry] = json.load(file)
        new_whitelsted_data: list[WhitelistedEntry] = []
        for player in whitelisted_data:
            player_uuid = player["uuid"]
            player_name = player["name"]

            if player_uuid in player_uuids or player_name in player_names:
                log.debug(f"Removed player '{player_name}' ({player_uuid}) from the whitelisted player list")
                continue

            new_whitelsted_data.append(player)

        file.seek(0)
        json.dump(new_whitelsted_data, file, indent=2)
        file.truncate()

# TODO: add 'update_player' and 'update_players', just use plain dict.update() because it has no depth

# List Players
def list_player() -> list[WhitelistedPlayer]:
    whitelisted_data: list[WhitelistedEntry] = json.loads(whitelisted_file.read_text())
    whitelisted_players: list[WhitelistedPlayer] = []
    for entry in whitelisted_data:
        whitelisted_player: WhitelistedPlayer = {
            "player_uuid": UUID(entry["uuid"]),
            "player_name": entry["name"]
        }

        whitelisted_players.append(whitelisted_player)

    return whitelisted_players
