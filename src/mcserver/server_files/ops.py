import json
import logging
from typing import TypedDict
from uuid import UUID

from .paths import ops_file_path
from .shared import update_file

logger = logging.getLogger(__name__)


class OperatorPlayer(TypedDict):
    player_uuid: UUID
    player_name: str
    permission_level: int
    bypasses_player_limit: bool


class OperatorFilePlayer(TypedDict):
    uuid: str
    name: str
    level: int
    bypassesPlayerLimit: bool


def list_players() -> list[OperatorPlayer]:
    """List all operator players

    Returns:
        List of operator players"""
    logger.debug(f"Reading {ops_file_path}")
    ops_json: list[OperatorFilePlayer] = json.loads(ops_file_path.read_text())

    operator_players: list[OperatorPlayer] = []
    for player in ops_json:
        operator_player: OperatorPlayer = {
            "player_uuid": UUID(player["uuid"]),
            "player_name": player["name"],
            "permission_level": player["level"],
            "bypasses_player_limit": player["bypassesPlayerLimit"],
        }

        operator_players.append(operator_player)

    return operator_players


def remove_players(
    player_uuids: list[UUID] | UUID | None = None,
    player_names: list[str] | str | None = None,
) -> list[OperatorPlayer]:
    """Remove operator players that matches either by UUIDs or names

    Args:
        player_uuids: List of player UUIDs to be removed
        player_names: List of player names to be removed

    Raises:
        FileNotFoundError: ops_file_path does not exist
        TypeError: ops_file_path's JSON root is not an array
        ValueError: Must provide at least a player UUID or player name

    Returns:
        List of operator players that are removed"""
    if not ops_file_path.exists():
        raise FileNotFoundError(f"File '{ops_file_path}' does not exist")

    ops_file_data = json.loads(ops_file_path.read_text())
    if not isinstance(ops_file_data, list):
        raise TypeError(f"JSON root of file '{ops_file_path}' is not an array")

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

    removed_players: list[OperatorPlayer] = []
    new_ops_data: list[OperatorFilePlayer] = []
    for operator_file_player in ops_file_data:
        if (
            UUID(operator_file_player["uuid"]) in uuids
            or operator_file_player["name"].lower() in names
        ):
            logger.debug(
                f"Operator player {operator_file_player['name']} ({operator_file_player['uuid']}) is removed"
            )
            operator_player: OperatorPlayer = {
                "player_uuid": UUID(operator_file_player["uuid"]),
                "player_name": operator_file_player["name"],
                "permission_level": operator_file_player["level"],
                "bypasses_player_limit": operator_file_player["bypassesPlayerLimit"],
            }

            removed_players.append(operator_player)
            continue

        new_ops_data.append(operator_file_player)

    if len(removed_players) == 0:
        logger.debug("No player is removed, skipping updating the file")
    else:
        update_file(ops_file_path, json.dumps(new_ops_data, indent=2).encode())

    return removed_players


def upsert_players(
    operator_players: list[OperatorPlayer] | OperatorPlayer,
) -> None:
    """Remove players and add them again (it sounds weird but its fine)

    Args:
        operator_players: List of players to be granted operator permission

    Raises:
        FileNotFoundError: whitelist_file_path does not exist
        TypeError: whitelist_file_path's JSON root is not an array"""
    if not ops_file_path.exists():
        raise FileNotFoundError(f"File '{ops_file_path}' does not exist")

    ops_file_data = json.loads(ops_file_path.read_text())
    if not isinstance(ops_file_data, list):
        raise TypeError(f"JSON root of file '{ops_file_path}' is not an array")

    if not isinstance(operator_players, list):
        operator_players = [operator_players]

    player_uuids: set[UUID] = set()
    player_names: set[str] = set()
    for operator_player in operator_players:
        player_uuids.add(operator_player["player_uuid"])
        player_names.add(operator_player["player_name"].lower())

    new_ops_file_data: list[OperatorFilePlayer] = []
    for operator_file_player in ops_file_data:
        if (
            UUID(operator_file_player["uuid"]) in player_uuids
            or operator_file_player["name"].lower() in player_names
        ):
            info_message = f"Operator player {operator_file_player['name']} ({operator_file_player['uuid']}) with level {operator_file_player['level']}"
            if operator_file_player["bypassesPlayerLimit"]:
                info_message += " and can bypass player limit"

            info_message += " is revoked"
            logger.debug(info_message)

            continue

        new_ops_file_data.append(operator_file_player)

    for operator_player in operator_players:
        operator_file_player: OperatorFilePlayer = {
            "uuid": str(operator_player["player_uuid"]),
            "name": operator_player["player_name"],
            "level": operator_player["permission_level"],
            "bypassesPlayerLimit": operator_player["bypasses_player_limit"],
        }

        info_message = f"Adding player {operator_player['player_name']} ({operator_player['player_uuid']}) to operator with level {operator_player['permission_level']}"
        if operator_player["bypasses_player_limit"]:
            info_message += " and can bypass player limit"

        logger.debug(info_message)
        new_ops_file_data.append(operator_file_player)

    update_file(ops_file_path, json.dumps(new_ops_file_data, indent=2).encode())
