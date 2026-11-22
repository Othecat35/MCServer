from ... import networking
from ...networking import ResponseObject
from ...urls import quiltmc_meta_url
from ..typings import Hashes, InstallerVersion


class GetInstallerVersionError(Exception):
    pass


def get_installer_versions() -> list[InstallerVersion]:
    response: ResponseObject = networking.request(
        f"{quiltmc_meta_url}/v3/versions/installer"
    )
    response_json: list | dict | None = response["json"]
    if response_json is None:
        raise GetInstallerVersionError("Response is not a JSON")
    elif not isinstance(response_json, list):
        raise GetInstallerVersionError("Response JSON is not a list")

    installer_versions: list[InstallerVersion] = []
    for version in response_json:
        version_hashes = version["hashes"]
        hashes: Hashes = {
            "sha1": version_hashes["sha1"],
            "sha256": version_hashes["sha256"],
            "sha512": version_hashes["sha512"],
        }

        installer_version: InstallerVersion = {
            "maven_coordinate": version["maven"],
            "version_string": version["version"],
            "download_url": version["url"],
            "file_size": version["file_size"],
            "hashes": hashes,
        }

        installer_versions.append(installer_version)

    return installer_versions
