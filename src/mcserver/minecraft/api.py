# Modules
# Standard
import json
from typing import NotRequired, TypedDict

from .. import networking
from ..constants import minecraft_api_url
# MCSe.rver
from .player_identity import PlayerUUID, normalize_player_uuid


# TypedDict
class PlayerIdentity(TypedDict):
    player_uuid: PlayerUUID
    player_name: str
    is_legacy: NotRequired[bool]
    is_demo: NotRequired[bool]


# Functions
def get_player_from_name(player_name: str) -> PlayerIdentity:
    response = networking.request(
        f"{minecraft_api_url}/minecraft/profile/lookup/name/{player_name}"
    )
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
        raise ValueError("Cannot query more than 10 player names at once")

    data_payload = json.dumps(player_names).encode("utf-8")
    response = networking.request(
        f"{minecraft_api_url}/minecraft/profile/lookup/bulk/byname",
        data=data_payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    response_json = json.loads(response["text"])

    player_identities: list[PlayerIdentity] = []
    for player in response_json:
        player_identity: PlayerIdentity = {
            "player_uuid": normalize_player_uuid(player["id"]),
            "player_name": player["name"],
        }

        if "legacy" in player:
            player_identity["is_legacy"] = player["legacy"]

        if "demo" in player:
            player_identity["is_demo"] = player["demo"]

        player_identities.append(player_identity)

    return player_identities


def get_player_from_uuid(player_uuid: PlayerUUID) -> PlayerIdentity:
    response = networking.request(
        f"{minecraft_api_url}/minecraft/profile/lookup/{player_uuid}"
    )
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
