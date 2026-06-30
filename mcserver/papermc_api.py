#Modules
# Standard
import json

from typing import TypedDict

# MCServer
from networking import request
from constants import papermc_base_api

#TypedDicts
class DownloadChecksums(TypedDict):
  sha256: str

class BuildDownload(TypedDict):
  file_name: str
  checksums: DownloadChecksums
  file_size: int
  download_url: str

class BuildCommit(TypedDict):
  commit_hash: str
  commit_time: str
  commit_message: str

class ProjectBuild(TypedDict):
  build_id: int
  build_time: str
  channel: str
  commits: list[BuildCommit]
  downloads: BuildDownload

#Functions
def get_build(project_name: str, game_version: str, build_id: int | str) -> ProjectBuild:
  response = json.loads(request(f"{papermc_base_api}/projects/{project_name}/versions/{game_version}/builds/{build_id}")["body"])

  build_commits = []
  for commit in response["commits"]:
    build_commits.append({
      "commit_hash": commit["sha"],
      "commit_time": commit["time"],
      "commit_message": commit["message"]
    })

  # NOTE: For now, it is hardcoded to only use the "server:default" 'prop'
  server_default = response["downloads"]["server:default"]

  return {
    "build_id": response["id"],
    "build_time": response["time"],
    "channel": response["channel"],
    "commits": build_commits,
    "downloads": {
      "file_name": server_default["name"],
      "checksums": {
        "sha256": server_default["checksums"]["sha256"]
      },
      "file_size": server_default["size"],
      "download_url": server_default["url"]
    }
  }

def get_latest_build(project_name: str, game_version: str) -> ProjectBuild:
  return get_build(project_name, game_version, "latest")
