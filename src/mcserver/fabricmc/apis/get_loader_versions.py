from ... import networking
from ...networking import ResponseObject
from ...urls import fabricmc_meta_url
from ..typings import LoaderVersion


class GetLoaderVersionsError(Exception):
    pass


def get_loader_versions() -> list[LoaderVersion]:
    response: ResponseObject = networking.request(
        f"{fabricmc_meta_url}/v2/versions/loader"
    )
    response_json: list | dict | None = response["json"]
    if response_json is None:
        raise GetLoaderVersionsError("Response is not a JSON")
    elif not isinstance(response_json, list):
        raise GetLoaderVersionsError("Response JSON is not a list")

    loader_versions: list[LoaderVersion] = []
    for version in response_json:
        loader_version: LoaderVersion = {
            "version_separator": version["separator"],
            "build_number": version["build"],
            "maven_coordinate": version["maven"],
            "version_string": version["version"],
            "is_stable": version["stable"],
        }

        loader_versions.append(loader_version)

    return loader_versions
