import logging
from typing import Literal

from ... import networking
from ...urls import papermc_fill_url
from ..shared import BUILD_CHANNEL
from ..typings import (
    BuildChannel,
    BuildCommit,
    BuildDownload,
    BuildInformation,
    FileHashes,
)

logger: logging.Logger = logging.getLogger(__name__)


class GetBuildInformationError(Exception):
    pass


def get_build_information(
    project_name: str, game_version: str, build_id: int | Literal["latest"]
) -> BuildInformation:
    response: networking.ResponseObject = networking.request(
        f"{papermc_fill_url}/v3/projects/{project_name}/versions/{game_version}/builds/{build_id}"
    )
    response_json: dict | list | None = response["json"]
    if response_json is None:
        raise GetBuildInformationError("Response is not a JSON")
    elif not isinstance(response_json, dict):
        raise GetBuildInformationError("Response JSON is not a dict")

    build_channel: BuildChannel = response_json["channel"]
    if build_channel not in BUILD_CHANNEL:
        logger.debug(f"Unknown 'build_channel': {build_channel}")

    build_downloads: dict[str, BuildDownload] = {}
    for property_name, download in response_json["downloads"].items():
        download_checksums = download["checksums"]
        file_hashes: FileHashes = {"sha256": download_checksums["sha256"]}

        build_downloads[property_name] = {
            "file_name": download["name"],
            "file_hashes": file_hashes,
            "file_size": download["size"],
            "download_url": download["url"],
        }

    build_commits: list[BuildCommit] = []
    for commit in response_json["commits"]:
        build_commit: BuildCommit = {
            "commit_hash": commit["sha"],
            "commit_time": commit["time"],
            "commit_message": commit["message"],
        }

        build_commits.append(build_commit)

    build_information: BuildInformation = {
        "build_id": response_json["id"],
        "build_time": response_json["time"],
        "build_channel": build_channel,
        "build_commits": build_commits,
        "build_downloads": build_downloads,
    }

    return build_information
