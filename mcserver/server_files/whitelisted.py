#Modules
# Standard
import json
from pathlib import Path
from typing import TypedDict
from uuid import UUID

# MCServer
from minecraft.player_identity import normalize_player_uuid, PlayerUUID

#Paths
whitelisted_file = Path("whitelisted.json")

#TypedDicts
class WhitelistedEntry(TypedDict):
    uuid: str
    name: str

class WhitelistedPlayer(TypedDict):
    player_uuid: PlayerUUID
    player_name: str

#Functions
def add_player(player_uuid: PlayerUUID, player_name: str) -> None:
    whitelisted_player: WhitelistedPlayer = {
        "player_uuid": player_uuid,
        "player_name": player_name
    }

    add_players(whitelisted_player)

def add_players(whitelisted_players: list[WhitelistedPlayer] | WhitelistedPlayer) -> None:
    if not isinstance(whitelisted_players, list):
        whitelisted_players = [whitelisted_players]

    with open(whitelisted_file, mode="r+") as file:
        whitelisted_data = json.load(file)

        for player in whitelisted_players:
            whitelisted_entry: WhitelistedEntry = {
                "uuid": str(normalize_player_uuid(player["player_uuid"])),
                "name": player["player_name"]
            }

            whitelisted_data.append(whitelisted_entry)

        file.seek(0)
        json.dump(whitelisted_data, file, indent=2)
        file.truncate()

def list_player() -> list[WhitelistedPlayer]:
    whitelisted_data: list[WhitelistedEntry] = json.loads(whitelisted_file.read_text())
    whitelisted_players: list[WhitelistedPlayer] = []
    for entry in whitelisted_data:
        whitelisted_player: WhitelistedPlayer = {
            "player_uuid": UUID(entry["uuid"]),
            "player_name": entry["name"]
        }

        whitelisted_players.append(whitelisted_player)

    return whitelisted_players