#Modules
from typing import NotRequired, TypedDict
from uuid import UUID

#Type Aliases
type PlayerUUID = UUID | str

#TypedDicts
class PlayerID(TypedDict):
    # Used for providing either player UUID and/or name
    player_uuid: NotRequired[PlayerUUID]
    player_name: NotRequired[str]

#Functions
def normalize_player_uuid(player_uuid: PlayerUUID) -> UUID:
    if isinstance(player_uuid, str):
        player_uuid = UUID(player_uuid)

    return player_uuid
