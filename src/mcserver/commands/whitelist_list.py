import logging
from argparse import Namespace

from ..paths import current_dir
from ..server_files import whitelist
from ..server_files.paths import whitelist_file_path
from ..shared import pluralize

logger = logging.getLogger(__name__)


def run(args: Namespace) -> int:
    if not whitelist_file_path.exists():
        logger.error(f"Whitelist file '{whitelist_file_path.relative_to(current_dir)}' does not exist")
        return 1

    whitelisted_players = whitelist.list_players()

    player_count: int = len(whitelisted_players)
    if player_count == 0:
        logger.info("There are no whitelisted player.")
        return 1

    player_list: list[str] = []
    for player in whitelisted_players:
        player_list.append(f"{player['player_name']} ({player['player_uuid']})")

    logger.info(
        f"There {pluralize('is', player_count)} {player_count} whitelisted {pluralize('player', player_count)}:"
    )

    player_list.sort()
    print("\n".join(player_list))
    return 0
