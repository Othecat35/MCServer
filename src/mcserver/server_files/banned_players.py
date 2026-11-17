# Modules
# Standard
import logging
from typing import Literal, TypedDict
from uuid import UUID

logger = logging.getLogger(__name__)

# TypedDicts
class BannedPlayerEntry(TypedDict):
    uuid: str
    name: str
    created: str  # Time Format: yyyy-MM-dd HH:mm:ss Z
    source: str
    expires: str | Literal["forever"]  # Time format: yyyy-MM-dd HH:mm:ss Z
    reason: str


class BannedPlayer(TypedDict):
    player_uuid: UUID
    player_name: str
    created_time: str  # Time format: yyyy-MM-dd HH:mm:ss Z
    ban_source: str
    expires_time: str | Literal["forever"]  # Time format: yyyy-MM-dd HH:mm:ss Z
    ban_reason: str
