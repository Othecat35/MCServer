import logging
from argparse import Namespace

from ..minecraft.player_identity import get_offline_player_identities
from ..server_files import whitelist
from ..server_files.whitelist import WhitelistedPlayer

logger = logging.getLogger(__name__)


def run(args: Namespace) -> int:
    players: list[str] = args.players

    is_offline = True

    whitelisted_players: list[WhitelistedPlayer] = []
    if is_offline:
        player_identities = get_offline_player_identities(players)
        for player_identity in player_identities:
            whitelisted_player: WhitelistedPlayer = {
                "player_uuid": player_identity["player_uuid"],
                "player_name": player_identity["player_name"],
            }

            whitelisted_players.append(whitelisted_player)

    whitelist.upsert_players(whitelisted_players)

    return 0
