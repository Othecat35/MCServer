import json
import logging
from typing import TypedDict

from ..minecraft.player_identity import PlayerUUID
from .paths import whitelist_file

logger = logging.getLogger(__name__)


class WhitelistedPlayer(TypedDict):
    player_uuid: PlayerUUID
    player_name: str


class WhitelistedFilePlayer(TypedDict):
    uuid: str
    name: str


def list_players() -> list[WhitelistedPlayer]:
    logger.debug(f"Reading whitelist file {whitelist_file}")
    whitelist_json = whitelist_file.read_text()
    whitelist_data: list[WhitelistedFilePlayer] = json.loads(whitelist_json)

    whitelisted_players: list[WhitelistedPlayer] = []
    for player in whitelist_data:
        whitelisted_player: WhitelistedPlayer = {
            "player_uuid": player["uuid"],
            "player_name": player["name"],
        }

        whitelisted_players.append(whitelisted_player)

    return whitelisted_players
