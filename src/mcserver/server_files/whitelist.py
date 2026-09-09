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
    player_uuid: PlayerUUID
    player_name: str


class WhitelistFileEntry(TypedDict):
    uuid: str
    name: str


# Functions
# Add Players
def add_player(player_uuid: PlayerUUID, player_name: str) -> None:
    whitelist_entry: WhitelistEntry = {
        "player_uuid": player_uuid,
        "player_name": player_name,
    }

    add_players(whitelist_entry)


def add_players(whitelist_entries: list[WhitelistEntry] | WhitelistEntry) -> None:
    """Add entries to the whitelist file
    Args:
        whitelist_entries: List of or an entry of player to be whitelisted

    Raises:
        FileNotFoundError: Whitelist file does not exist
        json.JSONDecodeError: Cannot parse JSON of whitelist data
    """
    if not whitelist_file.exists():
        raise FileNotFoundError(f"Whitelist file ({whitelist_file}) does not exist")

    if not isinstance(whitelist_entries, list):
        whitelist_entries = [whitelist_entries]

    with open(whitelist_file, mode="r+") as file:
        whitelist_json: list[WhitelistFileEntry] = json.load(file)

        for entry in whitelist_entries:
            whitelist_entry: WhitelistFileEntry = {
                "uuid": str(normalize_player_uuid(entry["player_uuid"])),
                "name": entry.get("player_name", ""),
            }

            whitelist_json.append(whitelist_entry)

        file.seek(0)
        json.dump(whitelist_json, file, indent=2)
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
    """Remove player entries matching the exact UUIDs or names

    Args:
        player_ids: Player UUIDs and/or names object

    Returns:
        None: Returns nothing

    Raises:
        FileNotFoundError: The 'whitelist.json' file not found
    """
    if not isinstance(player_ids, list):
        player_ids = [player_ids]

    player_uuids: set[PlayerUUID | None] = set()
    player_names: set[str | None] = set()
    for player_id in player_ids:
        if "player_uuid" in player_id:
            player_uuids.add(player_id["player_uuid"])

        if "player_name" in player_id:
            player_names.add(player_id["player_name"])

    if not whitelist_file.exists():
        raise FileNotFoundError(f"File '{whitelist_file}' is not found.")

    with open(whitelist_file, mode="r+") as file:
        whitelist_data: list[WhitelistFileEntry] = json.load(file)
        new_whitelist_data: list[WhitelistFileEntry] = []
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


# List Entries
def list_entries() -> list[WhitelistEntry]:
    """Return a list of whitelist entries from the whitelist file
    Raises:
        FileNotFoundError: Whitelist file does not exist
        json.JSONDecodeError: Cannot parse JSON of whitelist file

    Returns:
        List of whitelist entries
    """
    if not whitelist_file.exists():
        raise FileNotFoundError(f"Whitelist file ({whitelist_file}) does not exist")

    whitelist_data: str = whitelist_file.read_text()

    # NOTE: A custom TypedDict for entry from JSON with NotRequired so we can get notified for edge cases where the field does no exist
    whitelist_json: list[WhitelistFileEntry] = json.loads(whitelist_data)

    whitelist_entries: list[WhitelistEntry] = []
    for file_entry in whitelist_json:
        if "uuid" not in file_entry:
            log.warning("Invalid whitelist entry: missing 'uuid'")
            continue

        if "name" not in file_entry:
            log.warning("Invalid whitelist entry: missing 'name'")
            continue

        file_entry_uuid = file_entry["uuid"]

        try:
            whitelist_entry: WhitelistEntry = {
                "player_uuid": UUID(file_entry_uuid),
                "player_name": file_entry["name"],
            }
        except ValueError:
            log.error(f"Invalid UUID in whitelist: '{file_entry_uuid}'")
            continue

        whitelist_entries.append(whitelist_entry)

    return whitelist_entries
