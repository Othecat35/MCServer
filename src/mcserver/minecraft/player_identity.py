# Modules
import hashlib
import logging
from typing import TypedDict
from uuid import UUID

logger = logging.getLogger(__name__)

# TypedDicts
class PlayerIdentity(TypedDict):
    player_uuid: UUID
    player_name: str


def separate_uuids_and_names(player_ids: list[str]) -> tuple[list[UUID], list[str]]:
    player_uuids: list[UUID] = []
    player_names: list[str] = []
    for player_id in player_ids:
        try:
            player_uuids.append(UUID(player_id))
        except ValueError:
            player_names.append(player_id)

    return (player_uuids, player_names)

def get_offline_player_identities(
    player_names: list[str] | str,
) -> list[PlayerIdentity]:
    player_identities: list[PlayerIdentity] = []
    for player_name in player_names:
        offline_player = f"OfflinePlayer:{player_name}".encode()
        player_uuid: UUID = UUID(hashlib.md5(offline_player).hexdigest())
        logger.debug(f"Offline UUID for '{player_name}' is '{player_uuid}'")
        player_identity: PlayerIdentity = {
            "player_uuid": player_uuid,
            "player_name": player_name,
        }

        player_identities.append(player_identity)

    return player_identities
