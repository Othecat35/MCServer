#Modules
# Standard
import json
from typing import TypedDict

# MCServer
from mcserver import networking
from mcserver.constants import fabricmc_base_api

#TypedDict
class LoaderVersion(TypedDict):
    separator: str
    build_number: int
    maven: str
    loader_version: str
    is_stable: bool

#Functions
def get_loader_versions() -> list[LoaderVersion]:
    response = networking.request(f"{fabricmc_base_api}/v2/versions/loader")
    response_data = json.loads(response["body"])

    loader_versions = []
    for data in response_data:
        loader_versions.append({
            "separator": data["separator"],
            "build_number": data["build"],
            "maven": data["maven"],
            "loader_version": data["version"],
            "is_stable": data["stable"]
        })

    return loader_versions