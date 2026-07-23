#Modules
# Standard
import json
from typing import TypedDict

# MCServer
from .. import networking
from ..constants import quiltmc_meta_url

#TypedDicts
class Hashes(TypedDict):
    sha1: str
    sha256: str
    sha512: str

class LoaderVersion(TypedDict):
    separator: str        #this is the separator for the loader version
    build_id: int
    maven_id: str
    loader_version: str
    file_size: int
    hashes: VersionHashes #what's this?

# Functions
def get_loader_versions() -> list[LoaderVersion]:
    response = networking.request(f"{quiltmc_meta_url}/v3/versions/loader")
    response_json = json.loads(response["text"])

    loader_versions: list[LoaderVersion] = []
    for version in response_json:
        hashes: Hashes = {}
        for hash_algorithm, hash_value in version["hashes"].items():
            if hash_algorithm in ["sha1", "sha256", "sha512"]:
                hashes[hash_algorithm] = hash_value

        loader_version: LoaderVersion = {
            "separator": version["separator"],
            "build_id": version["build"],
            "maven_id": version["maven"],
            "loader_version": version["version"],
            "file_size": version["file_size"],
            "hashes": hashes
        }

        loader_versions.append(loader_version)

    return loader_versions
