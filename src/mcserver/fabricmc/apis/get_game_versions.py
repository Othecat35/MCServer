from ... import networking
from ...networking import ResponseObject
from ...urls import fabricmc_meta_url
from ..typings import GameVersion


class GetGameVersionsError(Exception):
    pass


def get_game_versions() -> list[GameVersion]:
    response: ResponseObject = networking.request(
        f"{fabricmc_meta_url}/v2/versions/game"
    )
    response_json: list | dict | None = response["json"]
    if response_json is None:
        raise GetGameVersionsError("Response is not a JSON")
    elif not isinstance(response_json, list):
        raise GetGameVersionsError("Response JSON is not a list")

    game_versions: list[GameVersion] = []
    for version in response_json:
        game_version: GameVersion = {
            "version_string": version["version"],
            "is_stable": version["stable"],
        }

        game_versions.append(game_version)

    return game_versions
