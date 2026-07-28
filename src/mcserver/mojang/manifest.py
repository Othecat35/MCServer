#Modules
# Standard
import json
from typing import TypedDict

# MCServer
from .. import networking
from ..constants import mojang_manifest_url

#TypedDict
class LatestVersion(TypedDict):
    release_version: str  #original: release
    snapshot_version: str #original: snapshot

class GameVersion(TypedDict):
    version_id: str       #original: id
    version_type: str     #original: type
    package_url: str      #original: url
    release_time: str     #original: releaseTime
    package_sha1: str     #original: sha1
    compliance_level: int #original: complianceLevel

class VersionManifest(TypedDict):
    latest_game_version: LatestVersion #original: latest
    game_versions: list[GameVersion]   #original: versions

#Functions
def get_version_manifest() -> VersionManifest:
    response = networking.request(f"{mojang_manifest_url}/mc/game/version_manifest_v2.json")
    response_json = json.loads(response["text"])

    latest_version = response_json["latest"]

    game_versions: list[GameVersion] = []
    for version in response_json["versions"]:
        game_version: GameVersion = {
            "version_id": version["id"],
            "version_type": version["type"],
            "release_time": version["releaseTime"],
            "package_url": version["url"],
            "package_sha1": version["sha1"],
            "compliance_level": version["complianceLevel"]
        }

        game_versions.append(game_version)

    version_manifest: VersionManifest ={
        "latest_game_version": {
            "release_version": latest_version["release"],
            "snapshot_version": latest_version["snapshot"]
        },
        "game_versions": game_versions
    }

    return version_manifest

def get_latest_release_version() -> str:
    return get_version_manifest()["latest_game_version"]["release_version"]

def get_latest_snapshot_version() -> str:
    return get_version_manifest()["latest_game_version"]["snapshot_version"]