# Modules
# Standard
import json
from typing import Literal, TypedDict

# MCServer
from .. import networking
from ..constants import papermc_api_url


# TypedDicts
class FileHashes(TypedDict):
    sha256: str  # original: sha256


class BuildProp(TypedDict):
    file_name: str  # original: name
    file_hashes: FileHashes  # original: checksums
    file_size: int  # original: size
    download_url: str  # original: url


class BuildCommit(TypedDict):
    commit_hash: str  # original: hash
    commit_time: str  # original: time
    commit_message: str  # original: message


class ProjectBuild(TypedDict):
    build_id: int  # original: id
    build_time: str  # original: time
    channel: str  # original: channel
    build_commits: list[BuildCommit]  # original: commits
    download_props: dict[str, BuildProp]  # original: downloads


# Functions
def get_project_build(
    project_name: str, game_version: str, build_id: int | Literal["latest"] = "latest"
) -> ProjectBuild:
    response = networking.request(
        f"{papermc_api_url}/v3/projects/{project_name}/versions/{game_version}/builds/{build_id}"
    )
    response_json = json.loads(response["text"])

    build_commits: list[BuildCommit] = []
    for commit in response_json["commits"]:
        build_commit: BuildCommit = {
            "commit_hash": commit["sha"],
            "commit_time": commit["time"],
            "commit_message": commit["message"],
        }

        build_commits.append(build_commit)

    download_props: dict[str, BuildProp] = {}
    for prop_name, prop_data in response_json["downloads"].items():
        download_prop: BuildProp = {
            "file_name": prop_data["name"],
            "file_hashes": prop_data["checksums"],
            "file_size": prop_data["size"],
            "download_url": prop_data["url"],
        }

        download_props[prop_name] = download_prop

    # NOTE: probably use the "server:default" prop

    project_build: ProjectBuild = {
        "build_id": response_json["id"],
        "build_time": response_json["time"],
        "channel": response_json["channel"],
        "build_commits": build_commits,
        "download_props": download_props,
    }

    return project_build


def get_latest_project_build(project_name: str, game_version: str) -> ProjectBuild:
    return get_project_build(project_name, game_version, "latest")
