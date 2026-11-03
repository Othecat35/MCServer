import json
import logging
from collections.abc import Sequence
from typing import TypedDict
from uuid import UUID

from ..minecraft.player_identity import normalize_player_uuid
from .paths import whitelist_file_path

logger = logging.getLogger(__name__)


class WhitelistedPlayer(TypedDict):
    player_uuid: UUID
    player_name: str


class WhitelistedFilePlayer(TypedDict):
    uuid: str
    name: str


def remove_players(
    player_uuids: Sequence[UUID | str] | UUID | str | None = None,
    player_names: list[str] | str | None = None,
) -> list[WhitelistedPlayer]:
    """Remove players from the whitelist that matches either by UUIDs or names

    Args:
        player_uuids: List of player UUIDs to be removed
        player_names: List of player names to be removed

    Raises:
        ValueError: Must provide at least a player UUID or player name

    Returns:
        List of whitelisted players that are removed"""
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

    removed_players: list[WhitelistedPlayer] = []
    with open(whitelist_file_path, mode="r+") as whitelist_file:
        whitelist_data: list[WhitelistedFilePlayer] = json.load(whitelist_file)

        new_whitelist_data: list[WhitelistedFilePlayer] = []
        for whitelisted_file_player in whitelist_data:
            if (
                UUID(whitelisted_file_player["uuid"]) in uuids
                or whitelisted_file_player["name"] in names
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

        whitelist_file.seek(0)
        json.dump(new_whitelist_data, whitelist_file, indent=2)
        whitelist_file.truncate()

    return removed_players


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
