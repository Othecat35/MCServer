import json
import logging
from typing import TypedDict

from ..minecraft.player_identity import PlayerUUID
from .paths import whitelist_file_path

logger = logging.getLogger(__name__)


class WhitelistedPlayer(TypedDict):
    player_uuid: PlayerUUID
    player_name: str


class WhitelistedFilePlayer(TypedDict):
    uuid: str
    name: str

def remove_players(player_uuids: list[str] | str | None = None, player_names: list[str] | str | None = None) -> list[WhitelistedPlayer]:
    """Remove players from the whitelist that matches either the UUIDs or names
    
    Args:
        player_uuids: List of player UUIDs to be removed
        player_names: List of player names to be removed
    
    Raises:
        ValueError: Must provide at least a player UUID or player name
    
    Returns:
        List of whitelisted players that are removed"""
    if player_uuids is None:
        player_uuids = []
    
    if player_names is None:
        player_names = []

    if isinstance(player_uuids, str):
        player_uuids = [player_uuids]

    if isinstance(player_names, str):
        player_names = [player_names]

    if not player_uuids and not player_names:
        raise ValueError("Must provide at least a player UUID or player name")

    uuids: set[str] = set(player_uuids)
    names: set[str] = set(player_names)

    removed_players: list[WhitelistedPlayer] = []
    with open(whitelist_file_path, mode="r+") as whitelist_file:
        whitelist_data: list[WhitelistedFilePlayer] = json.load(whitelist_file)

        new_whitelist_data: list[WhitelistedFilePlayer] = []
        for whitelisted_file_player in whitelist_data:
            if whitelisted_file_player["uuid"] in uuids or whitelisted_file_player["name"] in names:
                logger.debug(f"Whitelisted player {whitelisted_file_player['name']} ({whitelisted_file_player['uuid']}) is removed")
                whitelisted_player: WhitelistedPlayer = {
                    "player_uuid": whitelisted_file_player["uuid"],
                    "player_name": whitelisted_file_player["name"]
                }

                removed_players.append(whitelisted_player)
                continue

            new_whitelist_data.append(whitelisted_file_player)
        
        whitelist_file.seek(0)
        json.dump(new_whitelist_data, whitelist_file, indent=2)
        whitelist_file.truncate()

    return removed_players



# def remove_players(player_ids: list[PlayerID] | PlayerID) -> None:
#     """Remove player entries matching the exact UUIDs or names

#     Args:
#         player_ids: Player UUIDs and/or names object

#     Returns:
#         None: Returns nothing

#     Raises:
#         FileNotFoundError: The 'whitelist.json' file not found
#     """
#     if not isinstance(player_ids, list):
#         player_ids = [player_ids]

#     player_uuids: set[PlayerUUID | None] = set()
#     player_names: set[str | None] = set()
#     for player_id in player_ids:
#         if "player_uuid" in player_id:
#             player_uuids.add(player_id["player_uuid"])

#         if "player_name" in player_id:
#             player_names.add(player_id["player_name"])

#     if not whitelist_file.exists():
#         raise FileNotFoundError(f"File '{whitelist_file}' is not found.")

#     with open(whitelist_file, mode="r+") as file:
#         whitelist_data: list[WhitelistFileEntry] = json.load(file)
#         new_whitelist_data: list[WhitelistFileEntry] = []
#         for player in whitelist_data:
#             player_uuid = player["uuid"]
#             player_name = player["name"]

#             if player_uuid in player_uuids or player_name in player_names:
#                 log.debug(
#                     f"Removed player '{player_name}' ({player_uuid}) from the whitelisted player list"
#                 )
#                 continue

#             new_whitelist_data.append(player)

#         file.seek(0)
#         json.dump(new_whitelist_data, file, indent=2)
#         file.truncate()



def list_players() -> list[WhitelistedPlayer]:
    logger.debug(f"Reading whitelist file {whitelist_file_path}")
    whitelist_json = whitelist_file_path.read_text()
    whitelist_data: list[WhitelistedFilePlayer] = json.loads(whitelist_json)

    whitelisted_players: list[WhitelistedPlayer] = []
    for player in whitelist_data:
        whitelisted_player: WhitelistedPlayer = {
            "player_uuid": player["uuid"],
            "player_name": player["name"],
        }

        whitelisted_players.append(whitelisted_player)

    return whitelisted_players
