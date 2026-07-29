#Modules
# Standard
import json
from typing import TypedDict

# MCServer
from .. import networking
from ..constants import fabricmc_meta_url

#TypedDict
class LoaderVersion(TypedDict):
    separator: str
    build_id: int
    maven_id: str
    loader_version: str
    is_stable: bool

#Functions
def get_loader_versions() -> list[LoaderVersion]:
    response = networking.request(f"{fabricmc_meta_url}/v2/versions/loader")
    response_json = json.loads(response["text"])

    loader_versions: list[LoaderVersion] = []
    for version in response_json:
        loader_version: LoaderVersion = {
            "separator": version["separator"],
            "build_id": version["build"],
            "maven_id": version["maven"],
            "loader_version": version["version"],
            "is_stable": version["stable"]
        }

        loader_versions.append(loader_version)

    return loader_versions

def server_download_loader(game_version: str, loader_version: str, installer_version) -> str:
    return f"{fabricmc_meta_url}/v2/versions/loader/{loader_version}/{game_version}/{installer_version}/server/jar"
