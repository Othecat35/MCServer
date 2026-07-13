#Modules
# Standard
from pathlib import Path
from typing import Literal, TypedDict

# MCServer
from minecraft.player_identity import PlayerUUID

#Paths
banned_players_file = Path("banned-players.json")

#TypedDicts
class BannedPlayerEntry(TypedDict):
    uuid: PlayerUUID
    name: str
    created: str                      # yyyy-MM-dd HH:mm:ss Z
    source: str
    expires: Literal["forever"] | str #Time format: yyyy-MM-dd HH:mm:ss Z                     
    reason: str

class BannedPlayer(TypedDict):
    player_uuid: PlayerUUID
    player_name: str
    created_time: str                      #Time format: yyyy-MM-dd HH:mm:ss Z
    ban_source: str
    expires_time: Literal["forever"] | str #Time format: yyyy-MM-dd HH:mm:ss Z
    ban_reason: str