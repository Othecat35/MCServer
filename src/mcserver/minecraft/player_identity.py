# Modules
import hashlib
from typing import TypedDict
from uuid import UUID


# TypedDicts
class PlayerIdentity(TypedDict):
    player_uuid: UUID
    player_name: str


def get_offline_player_identities(
    player_names: list[str] | str,
) -> list[PlayerIdentity]:
    player_identities: list[PlayerIdentity] = []
    for player_name in player_names:
        offline_player = f"OfflinePlayer:{player_name}".encode()
        player_uuid: UUID = UUID(hashlib.md5(offline_player).hexdigest())
        player_identity: PlayerIdentity = {
            "player_uuid": player_uuid,
            "player_name": player_name,
        }

        player_identities.append(player_identity)

    return player_identities
