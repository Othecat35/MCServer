import logging
from argparse import Namespace

from .. import paths
from ..server_files import ops
from ..shared import pluralize

logger = logging.getLogger(__name__)


def op_list(args: Namespace) -> int:
    paths.update_working_dir(args.directory)
    if not paths.ops_file.exists():
        logger.error(
            f"Operator file '{paths.ops_file.relative_to(paths.current_dir, walk_up=True)}' does not exist"
        )
        return 1

    operator_players = ops.list_players()

    player_count = len(operator_players)
    if player_count == 0:
        logger.info("There's no operator player.")
        return 1

    player_list: list[str] = []
    for player in operator_players:
        player_list.append(
            f"{player['player_name']} ({player['player_uuid']}) Level: {player['permission_level']}"
        )

    logger.info(
        f"There {pluralize('is', player_count)} {player_count} {pluralize('operator', player_count)}:"
    )

    player_list.sort()
    print("\n".join(player_list))
    return 0
