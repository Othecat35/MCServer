#Modules
# Standard
from pathlib import Path
from typing import TypedDict

# MCServer
from minecraft.player_identity import PlayerUUID

#Paths
whitelisted_file = Path("whitelisted.json")

#TypedDicts
class WhitelistedPlayerEntry(TypedDict):
    uuid: PlayerUUID
    name: str

class WhitelistedPlayer(TypedDict):
    player_uuid: PlayerUUID
    player_name: str