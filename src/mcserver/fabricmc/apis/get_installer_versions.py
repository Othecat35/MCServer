from ... import networking
from ..typings import InstallerVersion
from ..urls import fabricmc_meta_url


class GetInstallerVersionError(Exception): pass

def get_installer_versions() -> list[InstallerVersion]:
    response = networking.request(f"{fabricmc_meta_url}/v2/versions/installer")
    response_json = response["json"]
    if response_json is None:
        raise GetInstallerVersionError("Response is not a JSON")
    elif not isinstance(response_json, list):
        raise GetInstallerVersionError("Response JSON is not a list")

    installer_versions: list[InstallerVersion] = []
    for version in response_json:
        installer_version: InstallerVersion = {
            "download_url": version["url"],
            "maven_coordinate": version["maven"],
            "version_string": version["version"],
            "is_stable": version["stable"]
        }

        installer_versions.append(installer_version)

    return installer_versions
