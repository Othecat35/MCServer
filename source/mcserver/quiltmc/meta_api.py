from typing import TypedDict

class VersionHashes(TypedDict):
    sha1: str
    sha256: str
    sha512: str

class LoaderVersion(TypedDict):
    separator: str
    build_id: int
    maven_id: str
    loader_version: str
    file_size: int
    hashes: VersionHashes #what's this?

def get_loader_versions() -> list[LoaderVersion]:
    loader_versions: list[LoaderVersion] = []
    return loader_versions
