# Modules
# Standard
import json
from typing import NotRequired
from uuid import UUID

from .. import networking
from ..constants import minecraft_api_url
from .player_identity import PlayerIdentity


class GetPlayerError(Exception):
    pass


# TypedDict
class PlayerProfile(PlayerIdentity):
    is_legacy: NotRequired[bool]
    is_demo: NotRequired[bool]


# Functions
def get_player_from_name(player_name: str) -> PlayerIdentity:
    response = networking.request(
        f"{minecraft_api_url}/minecraft/profile/lookup/name/{player_name}"
    )

    if "json" not in response:
        raise GetPlayerError("Response does not have JSON")

    response_json = response["json"]
    if not isinstance(response_json, dict):
        raise TypeError("Response JSON is not a dictionary")

    player_profile: PlayerProfile = {
        "player_uuid": UUID(response_json["id"]),
        "player_name": response_json["name"],
    }

    if "legacy" in response_json:
        player_profile["is_legacy"] = response_json["legacy"]

    if "demo" in response_json:
        player_profile["is_demo"] = response_json["demo"]

    return player_profile


def get_players_from_names(player_names: list[str] | str) -> list[PlayerProfile]:
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

    if "json" not in response:
        raise GetPlayerError("Response does not have JSON")

    response_json = response["json"]
    if not isinstance(response_json, list):
        raise TypeError("Response JSON is not a list")

    player_identities: list[PlayerProfile] = []
    for player in response_json:
        player_profile: PlayerProfile = {
            "player_uuid": UUID(player["id"]),
            "player_name": player["name"],
        }

        if "legacy" in player:
            player_profile["is_legacy"] = player["legacy"]

        if "demo" in player:
            player_profile["is_demo"] = player["demo"]

        player_identities.append(player_profile)

    return player_identities


def get_player_from_uuid(player_uuid: UUID) -> PlayerProfile:
    response = networking.request(
        f"{minecraft_api_url}/minecraft/profile/lookup/{player_uuid}"
    )

    if "json" not in response:
        raise GetPlayerError("Response does not have JSON")

    response_json = response["json"]
    if not isinstance(response_json, dict):
        raise TypeError("Response JSON is not a dictionary")

    player_profile: PlayerProfile = {
        "player_uuid": UUID(response_json["id"]),
        "player_name": response_json["name"],
    }

    if "legacy" in response_json:
        player_profile["is_legacy"] = response_json["legacy"]

    if "demo" in response_json:
        player_profile["is_demo"] = response_json["demo"]

    return player_profile
