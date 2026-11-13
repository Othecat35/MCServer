import logging
from argparse import Namespace

from ..minecraft.player_identity import separate_uuids_and_names
from ..paths import current_dir
from ..server_files import ops
from ..server_files.paths import ops_file_path
from ..shared import pluralize

logger = logging.getLogger(__name__)


def run(args: Namespace) -> int:
    if not ops_file_path.exists():
        logger.error(f"Operator file '{ops_file_path.relative_to(current_dir)}' does not exist")
        return 1
    player_ids: list[str] = args.players

    player_uuids, player_names = separate_uuids_and_names(player_ids)
    removed_players = ops.remove_players(player_uuids, player_names)

    player_count: int = len(removed_players)
    if player_count == 0:
        logger.info("No matching player found.")
        return 0

    player_list: list[str] = []
    for player in removed_players:
        player_list.append(
            f"{player['player_name']} ({player['player_uuid']}) Level: {player['permission_level']}"
        )

    logger.info(
        f"There {pluralize('is', player_count)} {player_count} operator {pluralize('player', player_count)} that {pluralize('is', player_count)} removed:"
    )

    player_list.sort()
    print("\n".join(player_list))
    return 0
