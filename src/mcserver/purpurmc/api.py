# Modules
# Standard
import json
from typing import Literal, TypedDict

# MCServer
from .. import networking
from ..constants import purpurmc_api_url


# TypedDicts
class BuildCommit(TypedDict):
    author_name: str  # original: author
    author_email: str  # original: email
    commit_message: str  # original: description
    commit_hash: str  # original: hash
    commit_time: int  # original: timestamp


class ProjectBuild(TypedDict):
    project_name: str  # original: project
    game_version: str  # original: version
    build_id: int  # original: build
    build_status: str  # original: result
    build_time: int  # original: timestamp
    build_duration: int  # original: duration
    build_commits: list[BuildCommit]  # original: commits
    metadata: dict  # original: metadata
    artifact_md5: str  # original: md5


# Functions
def get_project_build(
    project_name: str, game_version: str, build_version: int | Literal["latest"]
) -> ProjectBuild:
    response = networking.request(
        f"{purpurmc_api_url}/v2/{project_name}/{game_version}/{build_version}"
    )
    response_data = json.loads(response["text"])

    build_commits: list[BuildCommit] = []
    for commit in response_data["commits"]:
        build_commit: BuildCommit = {
            "author_name": commit["author"],
            "author_email": commit["email"],
            "commit_message": commit["description"],
            "commit_hash": commit["hash"],
            "commit_time": commit["timestamp"],
        }

        build_commits.append(build_commit)

    project_build: ProjectBuild = {
        "project_name": response_data["project"],
        "game_version": response_data["version"],
        "build_id": response_data["build"],
        "build_status": response_data["result"],
        "build_time": response_data["timestamp"],
        "build_duration": response_data["duration"],
        "build_commits": build_commits,
        "metadata": response_data["metadata"],
        "artifact_md5": response_data["md5"],
    }

    return project_build


def get_latest_project_build(project_name: str, game_version: str) -> ProjectBuild:
    return get_project_build(project_name, game_version, "latest")


def download_url(
    project_name: str, game_version: str, build_version: int | Literal["latest"]
) -> str:
    return (
        f"{purpurmc_api_url}/v2/{project_name}/{game_version}/{build_version}/download"
    )


def latest_download_url(project_name: str, game_version: str) -> str:
    return download_url(project_name, game_version, "latest")
