#Modules
# Standard
import json
from typing import NotRequired, TypedDict

# MCServer
from mcserver import networking
from mcserver.constants import minecraft_base_api
from .player_identity import normalize_player_uuid, PlayerUUID

#TypedDict
class PlayerIdentity(TypedDict):
    player_uuid: PlayerUUID
    player_name: str
    is_legacy: NotRequired[bool]
    is_demo: NotRequired[bool]

#Functions
def get_player_from_name(player_name: str) -> PlayerIdentity:
    response = networking.request(f"{minecraft_base_api}/minecraft/profile/lookup/name/{player_name}")
    response_json = json.loads(response["text"])

    player_identity: PlayerIdentity = {
        "player_uuid": normalize_player_uuid(response_json["id"]),
        "player_name": response_json["name"],
    }

    if "legacy" in response_json:
        player_identity["is_legacy"] = response_json["legacy"]

    if "demo" in response_json:
        player_identity["is_demo"] = response_json["demo"]

    return player_identity

def get_players_from_names(player_names: list[str] | str) -> list[PlayerIdentity]:
    if isinstance(player_names, str):
        player_names = [player_names]

    if len(player_names) > 10:
        raise ValueError("Cannot query more than 10 players names at once")

    data_payload = json.dumps(player_names).encode("utf-8")
    response = networking.request(f"{minecraft_base_api}/minecraft/profile/lookup/bulk/byname", data=data_payload, headers={
        "Content-Type": "application/json"
    }, method="POST")

    response_json = json.loads(response["text"])

    player_identities = []
    for data in response_json:
        player_identity = {
            "player_uuid": normalize_player_uuid(data["id"]),
            "player_name": data["name"],
        }

        if "legacy" in data: player_identity["is_legacy"] = data["legacy"]
        if "demo" in data: player_identity["is_demo"] = data["demo"]
        player_identities.append(player_identity)

    return player_identities

def get_player_from_uuid(player_uuid: PlayerUUID) -> PlayerIdentity:
    response = networking.request(f"{minecraft_base_api}/minecraft/profile/lookup/{player_uuid}")
    response_data = json.loads(response["text"])

    player_identity: PlayerIdentity = {
        "player_uuid": normalize_player_uuid(response_data["id"]),
        "player_name": response_data["name"],
    }

    if "legacy" in response_data: player_identity["is_legacy"] = response_data["legacy"]
    if "demo" in response_data: player_identity["is_demo"] = response_data["demo"]
    return player_identity
