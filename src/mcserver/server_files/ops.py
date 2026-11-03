import json
import logging
from collections.abc import Sequence
from typing import TypedDict
from uuid import UUID

from ..minecraft.player_identity import normalize_player_uuid
from .paths import ops_file_path

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


def remove_players(
    player_uuids: Sequence[UUID | str] | UUID | str | None = None,
    player_names: list[str] | str | None = None,
) -> list[OperatorPlayer]:
    """Remove operator players that matches either by UUIDs or names

    Args:
        player_uuids: List of player UUIDs to be removed
        player_names: List of player names to be removed

    Raises:
        ValueError: Must provide at least a player UUID or player name

    Returns:
        List of operator players that are removed"""
    if player_uuids is None:
        player_uuids = []
    elif isinstance(player_uuids, (UUID, str)):
        player_uuids = [player_uuids]

    if player_names is None:
        player_names = []
    elif isinstance(player_names, str):
        player_names = [player_names]

    if not player_uuids and not player_names:
        raise ValueError("Must provide at least a player UUID or player name")

    names: set[str] = set(player_names)

    uuids: set[UUID] = set()
    for player_uuid in player_uuids:
        uuids.add(normalize_player_uuid(player_uuid))

    removed_players: list[OperatorPlayer] = []
    with open(ops_file_path, mode="r+") as ops_file:
        ops_data: list[OperatorFilePlayer] = json.load(ops_file)

        new_ops_data: list[OperatorFilePlayer] = []
        for operator_file_player in ops_data:
            if (
                UUID(operator_file_player["uuid"]) in uuids
                or operator_file_player["name"] in names
            ):
                logger.debug(
                    f"Operator player {operator_file_player['name']} ({operator_file_player['uuid']}) is removed"
                )
                operator_player: OperatorPlayer = {
                    "player_uuid": UUID(operator_file_player["uuid"]),
                    "player_name": operator_file_player["name"],
                    "permission_level": operator_file_player["level"],
                    "bypasses_player_limit": operator_file_player[
                        "bypassesPlayerLimit"
                    ],
                }

                removed_players.append(operator_player)
                continue

            new_ops_data.append(operator_file_player)

        ops_file.seek(0)
        json.dump(new_ops_data, ops_file, indent=2)
        ops_file.truncate()

    return removed_players


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
