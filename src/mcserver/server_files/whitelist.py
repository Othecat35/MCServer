import json
import logging
from typing import TypedDict
from uuid import UUID

from ..minecraft.player_identity import PlayerIdentity
from ..shared import update_file
from .paths import whitelist_file_path

logger = logging.getLogger(__name__)


class WhitelistedPlayer(PlayerIdentity):
    pass


class WhitelistedFilePlayer(TypedDict):
    uuid: str
    name: str


def list_players() -> list[WhitelistedPlayer]:
    logger.debug(f"Reading whitelist file {whitelist_file_path}")
    whitelist_data: list[WhitelistedFilePlayer] = json.loads(
        whitelist_file_path.read_text()
    )

    whitelisted_players: list[WhitelistedPlayer] = []
    for player in whitelist_data:
        whitelisted_player: WhitelistedPlayer = {
            "player_uuid": UUID(player["uuid"]),
            "player_name": player["name"],
        }

        whitelisted_players.append(whitelisted_player)

    return whitelisted_players


def remove_players(
    player_uuids: list[UUID] | UUID | None = None,
    player_names: list[str] | str | None = None,
) -> list[WhitelistedPlayer]:
    """Remove players from the whitelist that matches either by UUIDs or names
    Skip writing if nothing chnaged

    Args:
        player_uuids: List of player UUIDs to be removed
        player_names: List of player names to be removed

    Raises:
        FileNotFoundError: whitelist_file_path does not exist
        TypeError: whitelist_file_path's JSON root is not an array
        ValueError: Must provide at least a player UUID or a player name

    Returns:
        List of whitelisted players that are removed"""
    if not whitelist_file_path.exists():
        raise FileNotFoundError(f"File '{whitelist_file_path}' does not exist")

    whitelist_file_data = json.loads(whitelist_file_path.read_text())
    if not isinstance(whitelist_file_data, list):
        raise TypeError(f"JSON root of file '{whitelist_file_path}' is not an array")

    if player_uuids is None:
        player_uuids = []
    elif not isinstance(player_uuids, list):
        player_uuids = [player_uuids]

    if player_names is None:
        player_names = []
    elif not isinstance(player_names, list):
        player_names = [player_names]

    if player_uuids == [] and player_names == []:
        raise ValueError("Must provide at least a player UUID or a player name")

    uuids: set[UUID] = set(player_uuids)
    names: set[str] = set()
    for player_name in player_names:
        names.add(player_name.lower())

    removed_players: list[WhitelistedPlayer] = []
    new_whitelist_data: list[WhitelistedFilePlayer] = []
    for whitelisted_file_player in whitelist_file_data:
        if (
            UUID(whitelisted_file_player["uuid"]) in uuids
            or whitelisted_file_player["name"].lower() in names
        ):
            logger.debug(
                f"Whitelisted player {whitelisted_file_player['name']} ({whitelisted_file_player['uuid']}) is removed"
            )
            whitelisted_player: WhitelistedPlayer = {
                "player_uuid": UUID(whitelisted_file_player["uuid"]),
                "player_name": whitelisted_file_player["name"],
            }

            removed_players.append(whitelisted_player)
            continue

        new_whitelist_data.append(whitelisted_file_player)

    if len(removed_players) == 0:
        logger.debug("No player is removed, skipping updating the file")
    else:
        update_file(
            whitelist_file_path, json.dumps(new_whitelist_data, indent=2).encode()
        )

    return removed_players


def upsert_players(
    whitelisted_players: list[WhitelistedPlayer] | WhitelistedPlayer,
) -> None:
    """Remove players and add them again (it sounds weird but its fine)

    Args:
        whitelisted_players: List of players to be whitelisted

    Raises:
        FileNotFoundError: whitelist_file_path does not exist
        TypeError: whitelist_file_path's JSON root is not an array"""
    if not whitelist_file_path.exists():
        raise FileNotFoundError(f"File '{whitelist_file_path}' does not exist")

    whitelist_file_data = json.loads(whitelist_file_path.read_text())
    if not isinstance(whitelist_file_data, list):
        raise TypeError(f"JSON root of file '{whitelist_file_path}' is not an array")

    if not isinstance(whitelisted_players, list):
        whitelisted_players = [whitelisted_players]

    player_uuids: set[UUID] = set()
    player_names: set[str] = set()
    for whitelisted_player in whitelisted_players:
        player_uuids.add(whitelisted_player["player_uuid"])
        player_names.add(whitelisted_player["player_name"].lower())

    new_whitelist_file_data: list[WhitelistedFilePlayer] = []
    for whitelisted_file_player in whitelist_file_data:
        if (
            UUID(whitelisted_file_player["uuid"]) in player_uuids
            or whitelisted_file_player["name"].lower() in player_names
        ):
            logger.debug(
                f"Whitelisted player {whitelisted_file_player['name']} ({whitelisted_file_player['uuid']}) is removed"
            )

            continue

        new_whitelist_file_data.append(whitelisted_file_player)

    for whitelisted_player in whitelisted_players:
        whitelisted_file_player: WhitelistedFilePlayer = {
            "uuid": str(whitelisted_player["player_uuid"]),
            "name": whitelisted_player["player_name"],
        }

        logger.debug(
            f"Adding player {whitelisted_player['player_name']} ({whitelisted_player['player_uuid']}) to the whitelist"
        )
        new_whitelist_file_data.append(whitelisted_file_player)

    update_file(
        whitelist_file_path, json.dumps(new_whitelist_file_data, indent=2).encode()
    )
