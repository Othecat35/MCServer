import logging
from argparse import Namespace
from uuid import UUID

from ..minecraft.player_identity import separate_uuids_and_names
from ..server_files.ops import OperatorPlayer

logger = logging.getLogger(__name__)


def run(args: Namespace) -> int:
    player_ids: list[str] = args.players
    online_mode: str | None = args.online_mode
    permission_level: int | None = args.permission_level
    bypasses_player_limit: bool = args.bypasses_player_limit

    # UUID vs name seperator
    player_uuids, player_names = separate_uuids_and_names(player_ids)
    uuids: set[UUID] = set(player_uuids)
    names: set[str] = set(player_names)

    player_uuids: list[UUID] = list(uuids)
    player_names: list[str] = list(names)

    is_online_mode: bool = True
    if online_mode is None:
        from ..server_files import server_properties
        is_online_mode = server_properties.get_online_mode()
    else:
        is_online_mode = online_mode != "false"
    
    if permission_level is None:
        from ..server_files import server_properties
        permission_level = server_properties.get_operator_permission_level()

    operator_players: list[OperatorPlayer] = []
    if is_online_mode:
        from ..minecraft import api as minecraft_api
        for player_uuid in player_uuids:
            player_profile = minecraft_api.get_player_from_uuid(player_uuid)
            operator_player: OperatorPlayer = {
                "player_uuid": player_profile["player_uuid"],
                "player_name": player_profile["player_name"],
                "permission_level": permission_level,
                "bypasses_player_limit": bypasses_player_limit
            }

            operator_players.append(operator_player)
        if len(player_names) > 10:
            logger.error("Cannot add more than 10 players by name at once.")
            return 1

        player_profiles = minecraft_api.get_players_from_names(player_names)
        for player_profile in player_profiles:
            operator_player: OperatorPlayer = {
                "player_uuid": player_profile["player_uuid"],
                "player_name": player_profile["player_name"],
                "permission_level": permission_level,
                "bypasses_player_limit": bypasses_player_limit
            }

            operator_players.append(operator_player)
    else:
        for player_uuid in uuids:
            logger.error(f"Cannot add by UUID in offline mode: {player_uuid}, use name instead.")
            return 1

        from ..minecraft.player_identity import get_offline_player_identities
        player_profiles = get_offline_player_identities(player_names)
        for player_profile in player_profiles:
            operator_player: OperatorPlayer = {
                "player_uuid": player_profile["player_uuid"],
                "player_name": player_profile["player_name"],
                "permission_level": permission_level,
                "bypasses_player_limit": bypasses_player_limit
            }

            operator_players.append(operator_player)

    from ..server_files import ops
    ops.upsert_players(operator_players)
    
    from ..shared import pluralize
    player_count: int = len(operator_players)
    if player_count == 0:
        logger.info("There are no player to be granted operator.")
        return 0

    player_list: list[str] = []
    for player in operator_players:
        player_list.append(f"{player['player_name']} ({player['player_uuid']})")

    info_message = f"Granted {player_count} {pluralize('player', player_count)} operator with permission level {permission_level}"

    if bypasses_player_limit:
        info_message += " and can bypass player limit"

    info_message += ":"
    logger.info(info_message)

    player_list.sort()
    print("\n".join(player_list))
    return 0
