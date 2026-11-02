import argparse
import logging

from ..server_files import whitelist
from ..shared import pluralize

logger = logging.getLogger(__name__)


def run(args: argparse.Namespace) -> int:
    whitelist_file = whitelist.whitelist_file
    if not whitelist_file.exists():
        logger.error(f"Whitelist file ({whitelist_file}) does not exist!")
        return 1

    whitelisted_players = whitelist.list_players()

    player_list: list[str] = []
    for player in whitelisted_players:
        player_list.append(f"{player['player_name']} ({player['player_uuid']})")

    player_count: int = len(player_list)
    if player_count == 0:
        logger.info("There are no whitelisted players.")
        return 0
    else:
        logger.info(
            f"There {pluralize('is', player_count)} whitelisted {pluralize('player', player_count)}:"
        )

    player_list.sort()
    print("\n".join(player_list))
    return 0
