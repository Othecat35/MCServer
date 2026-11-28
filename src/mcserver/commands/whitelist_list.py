import logging
from argparse import Namespace

from .. import paths
from ..server_files import whitelist
from ..shared import pluralize

logger = logging.getLogger(__name__)


def whitelist_list(args: Namespace) -> int:
    paths.update_working_dir(args.directory)
    if not paths.whitelist_file.exists():
        logger.error(
            f"Whitelist file '{paths.whitelist_file.relative_to(paths.current_dir, walk_up=True)}' does not exist"
        )
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
