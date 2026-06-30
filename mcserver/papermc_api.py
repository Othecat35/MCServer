#Modules
# Standard
import json

from typing import Literal, TypedDict

# MCServer
from networking import request
from constants import papermc_base_api

#TypedDicts
class DownloadChecksums(TypedDict):
  sha256: str #original: sha256

class BuildProp(TypedDict):
  file_name: str               #original: name
  checksums: DownloadChecksums #original: checksums
  file_size: int               #original: size
  download_url: str            #original: url

class BuildCommit(TypedDict):
  commit_hash: str    #original: hash
  commit_time: str    #original: time
  commit_message: str #original: message

class ProjectBuild(TypedDict):
  build_version: int                    #original: id
  build_time: str                       #original: time
  channel: str                          #original: channel
  build_commits: list[BuildCommit]      #original: commits
  download_props: dict[str, BuildProp]  #original: downloads

#Functions
def get_project_build(project_name: str, game_version: str, build_id: int | Literal["latest"]) -> ProjectBuild:
  response = request(f"{papermc_base_api}/v3/projects/{project_name}/versions/{game_version}/builds/{build_id}")
  response_data = json.loads(response["body"])

  build_commits = []
  for commit in response_data["commits"]:
    build_commits.append({
      "commit_hash": commit["sha"],
      "commit_time": commit["time"],
      "commit_message": commit["message"]
    })

  download_props = {}
  for prop_name, prop_data in response_data["downloads"].items():
    download_props[prop_name] = {
      "file_name": prop_data["name"],
      "checksums": prop_data["checksums"],
      "file_size": prop_data["size"],
      "download_url": prop_data["url"]
    }

  # NOTE: probably use the "server:default" prop

  return {
    "build_version": response_data["id"],
    "build_time": response_data["time"],
    "channel": response_data["channel"],
    "build_commits": build_commits,
    "download_props": download_props
  }

def get_latest_project_build(project_name: str, game_version: str) -> ProjectBuild:
  return get_project_build(project_name, game_version, "latest")
