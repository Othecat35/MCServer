from ... import networking
from ..typings import Hashes, LoaderVersion
from ..urls import quiltmc_api_url


class GetLoaderVersionsError(Exception):
    pass


def get_loader_versions() -> list[LoaderVersion]:
    response = networking.request(f"{quiltmc_api_url}/v3/versions/loader")
    response_json = response["json"]
    if response_json is None:
        raise GetLoaderVersionsError("Response is not a JSON")
    elif not isinstance(response_json, list):
        raise GetLoaderVersionsError("Response JSON is not a list")

    loader_versions: list[LoaderVersion] = []
    for version in response_json:
        version_hashes = version["hashes"]
        hashes: Hashes = {
            "sha1": version_hashes["sha1"],
            "sha256": version_hashes["sha256"],
            "sha512": version_hashes["sha512"],
        }

        loader_version: LoaderVersion = {
            "maven_coordinate": version["maven"],
            "version": version["version"],
            "build_number": version["build"],
            "version_separator": version["separator"],
            "file_size": version["file_size"],
            "hashes": hashes,
        }

        loader_versions.append(loader_version)

    return loader_versions
