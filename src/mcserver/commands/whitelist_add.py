import logging
from argparse import Namespace

from ..minecraft.player_identity import separate_uuids_and_names
from ..server_files import whitelist
from ..server_files.whitelist import WhitelistedPlayer

logger = logging.getLogger(__name__)


def run(args: Namespace) -> int:
    player_ids: list[str] = args.players
    online_mode: str | None = args.online_mode

    # UUID vs name seperator
    player_uuids, player_names = separate_uuids_and_names(player_ids)

    is_online_mode: bool = True
    if online_mode is None:
        # lazy loading because it isn't necessarily imported
        from pathlib import Path

        server_properties_file_path = Path("server.properties")
        if server_properties_file_path.exists():
            logger.debug("server.properties does exist")
            from ..server_files import properties
            server_properties = properties.loads(server_properties_file_path.read_text())
            server_online_mode = server_properties["data"].get("online-mode", "true")
            is_online_mode = server_online_mode != "false"

    else:
        is_online_mode = online_mode != "false"

    logger.debug(f"is_online_mode is set to {is_online_mode}")
    whitelisted_players: list[WhitelistedPlayer] = []
    if is_online_mode:
        from ..minecraft import api as minecraft_api
        player_profiles = minecraft_api.get_players_from_names(players)
        player_names: set[str] = set()
        for player_profile in player_profiles:
            whitelisted_player: WhitelistedPlayer = {
                "player_uuid": player_profile["player_uuid"],
                "player_name": player_profile["player_name"]
            }

            player_names.add(player_profile["player_name"])
            whitelisted_players.append(whitelisted_player)
    else:
        from ..minecraft.player_identity import get_offline_player_identities
        whitelisted_players = get_offline_player_identities(players)

    whitelist.upsert_players(whitelisted_players)

    return 0
