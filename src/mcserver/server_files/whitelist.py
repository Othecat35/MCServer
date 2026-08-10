# Modules
# Standard
import json
import logging as log
from pathlib import Path
from typing import TypedDict
from uuid import UUID

# MCServer
from mcserver.minecraft.player_identity import (
    PlayerID,
    PlayerUUID,
    normalize_player_uuid,
)

# Paths
whitelist_file = Path("whitelist.json")


# TypedDicts
class WhitelistEntry(TypedDict):
    uuid: str
    name: str


class WhitelistPlayer(TypedDict):
    player_uuid: PlayerUUID
    player_name: str


# Functions
# Add Players
def add_player(player_uuid: PlayerUUID, player_name: str) -> None:
    whitelist_player: WhitelistPlayer = {
        "player_uuid": player_uuid,
        "player_name": player_name,
    }

    add_players(whitelist_player)


def add_players(whitelist_players: list[WhitelistPlayer] | WhitelistPlayer) -> None:
    if not isinstance(whitelist_players, list):
        whitelist_players = [whitelist_players]

    with open(whitelist_file, mode="r+") as file:
        whitelist_data = json.load(file)

        for player in whitelist_players:
            whitelist_entry: WhitelistEntry = {
                "uuid": str(normalize_player_uuid(player["player_uuid"])),
                "name": player.get("player_name", ""),
            }

            whitelist_data.append(whitelist_entry)

        file.seek(0)
        json.dump(whitelist_data, file, indent=2)
        file.truncate()


# Remove Players
def remove_player(
    player_uuid: PlayerUUID | None = None, player_name: str | None = None
) -> None:
    if player_uuid is None and player_name is None:
        raise ValueError(
            "At least one of 'player_uuid' or 'player_name' must be provided"
        )

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

    with open(whitelist_file, mode="r+") as file:
        whitelist_data: list[WhitelistEntry] = json.load(file)
        new_whitelist_data: list[WhitelistEntry] = []
        for player in whitelist_data:
            player_uuid = player["uuid"]
            player_name = player["name"]

            if player_uuid in player_uuids or player_name in player_names:
                log.debug(
                    f"Removed player '{player_name}' ({player_uuid}) from the whitelisted player list"
                )
                continue

            new_whitelist_data.append(player)

        file.seek(0)
        json.dump(new_whitelist_data, file, indent=2)
        file.truncate()


# TODO: add 'update_player' and 'update_players', just use plain dict.update() because it has no depth


# List Players
def list_players() -> list[WhitelistPlayer]:
    whitelist_data: list[WhitelistEntry] = json.loads(whitelist_file.read_text())

    whitelist_players: list[WhitelistPlayer] = []
    for entry in whitelist_data:
        player_uuid: str | None = entry.get("uuid", None)
        player_name: str | None = entry.get("name", None)

        if player_uuid is None or player_name is None:
            error_message = f"Invalid whitelist entry!"
            if player_uuid:
                error_message += f" UUID: '{player_uuid}'"

            if player_name:
                error_message += f" Name: '{player_name}'"

            log.error(error_message)
            continue

        try:
            whitelist_player: WhitelistPlayer = {
                "player_uuid": UUID(player_uuid),
                "player_name": entry["name"],
            }
        except ValueError:
            log.error(f"Invalid UUID in whitelist: '{player_uuid}'")
            continue

        whitelist_players.append(whitelist_player)

    return whitelist_players
