import json

from typing import TypedDict

from network import request_url
from constants import papermc_api_base

# TypedDicts
class BuildCommit(TypedDict):
  commit_hash: str
  commit_time: str
  message: str

class DownloadChecksum(TypedDict):
  sha256: str

class BuildDownload(TypedDict):
  file_name: str
  checksums: DownloadChecksum
  file_size: int
  download_url: str

class ProjectBuild(TypedDict):
  build_id: int
  build_time: str
  channel: str
  commits: list[BuildCommit]
  download: BuildDownload

# Functions
def get_latest_build(project_name: str, game_version: str) -> ProjectBuild:
  build_data = request_url(f"{papermc_api_base}v3/projects/{project_name}/versions/{game_version}/builds/latest")["text"]

  build_commits = []
  for commit in build_data["commits"]:
    build_commits.append({
      "commit_hash": commit["hash"],
      "commit_time": commit["time"],
      "message": commit["message"]
    })

  build_download = build_data["downloads"]["server:default"]

  return {
    "build_id": build_data["id"],
    "build_time": build_data["time"],
    "channel": build_data["channel"],
    "commits": build_commits,
    "download": {
      "file_name": build_download["name"],
      "checksums": {
        "sha256": build_download["checksums"]["sha256"]
      },
      "file_size": build_download["size"],
      "download_url": build_download["url"]
    }
  }