from ... import networking
from ..typings import GameVersion
from ..urls import fabricmc_meta_url


class GetGameVersionError(Exception): pass

def get_game_versions() -> list[GameVersion]:
    response = networking.request(f"{fabricmc_meta_url}/v2/versions/game")
    response_json = response["json"]
    if response_json is None:
        raise GetGameVersionError("Response is not a JSON")
    elif not isinstance(response_json, list):
        raise GetGameVersionError("Response JSON is not a list")

    game_versions: list[GameVersion] = []
    for version in response_json:
        game_version: GameVersion = {
            "version_string": version["version"],
            "is_stable": version["stable"]
        }

        game_versions.append(game_version)

    return game_versions
