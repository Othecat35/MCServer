# Modules
# Standard
import json
from typing import TypedDict

# MCServer
from .. import networking
from ..constants import quiltmc_meta_url


# TypedDicts
class Hashes(TypedDict):
    sha1: str
    sha256: str
    sha512: str


class LoaderVersion(TypedDict):
    separator: str  # this is the separator for the loader version
    build_id: int
    maven_id: str
    loader_version: str
    file_size: int
    hashes: (
        Hashes  # what hash is this for? I don't know, please future me figure it out :>
    )


# Functions
def get_loader_versions() -> list[LoaderVersion]:
    response = networking.request(f"{quiltmc_meta_url}/v3/versions/loader")
    response_json = json.loads(response["text"])

    loader_versions: list[LoaderVersion] = []
    for version in response_json:
        version_hash = version["hashes"]
        hashes: Hashes = {
            "sha1": version_hash["sha1"],
            "sha256": version_hash["sha256"],
            "sha512": version_hash["sha512"],
        }

        loader_version: LoaderVersion = {
            "separator": version["separator"],
            "build_id": version["build"],
            "maven_id": version["maven"],
            "loader_version": version["version"],
            "file_size": version["file_size"],
            "hashes": hashes,
        }

        loader_versions.append(loader_version)

    return loader_versions
