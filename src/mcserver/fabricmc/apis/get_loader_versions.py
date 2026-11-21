from ... import networking
from ...networking import ResponseObject
from ...urls import fabricmc_meta_url
from ..typings import LoaderVersion


class GetLoaderVersionsError(Exception): pass

def get_loader_versions(game_version: str | None = None, loader_version: str | None = None) -> list[LoaderVersion]:
    if game_version is None and loader_version is not None:
        raise ValueError("Must provide value for 'game_version' when using 'loader_version'")

    request_url: str = f"{fabricmc_meta_url}/v2/versions/loader"
    if game_version is not None:
        request_url += f"/{game_version}"
        if loader_version is not None:
            request_url += f"/{loader_version}"

    response: ResponseObject = networking.request(request_url)
    response_json: list | dict | None = response["json"]
    if response_json is None:
        raise GetLoaderVersionsError("Response is not a JSON")
    elif not isinstance(response_json, list):
        raise GetLoaderVersionsError("Response JSON is not a list")

    loader_versions: list[LoaderVersion] = []
    for version in response_json:
        loader_version_data: LoaderVersion = {
            "version_separator": version["separator"],
            "build_number": version["build"],
            "maven_coordinate": version["maven"],
            "version_string": version["version"],
            "is_stable": version["stable"]
        }

        loader_versions.append(loader_version_data)

    return loader_versions
