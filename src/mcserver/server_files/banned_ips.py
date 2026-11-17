# Modules
# Standard
import logging
from typing import Literal, TypedDict

logger = logging.getLogger(__name__)


# TypedDicts
class BannedIPEntry(TypedDict):
    ip: str | Literal["<unknown>"]  # IPv4 or IPv6
    created: str  # Time format: yyyy-MM-dd HH:mm:ss Z
    source: str
    expires: Literal["forever"] | str  # Time Format:  yyyy-MM-dd HH:mm:ss Z
    reason: str


class BannedIPRecord(TypedDict):
    ip_address: str  # IPv4 or IPv6
    created_time: str  # Time format: yyyy-MM-dd HH:mm:ss Z
    ban_source: str
    expires_time: str | Literal["forever"]  # Time format: yyyy-MM-dd HH:mm:ss Z
    ban_reason: str
