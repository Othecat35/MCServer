#Modules
# Standard
import json
from typing import Literal, TypedDict

# MCServer
from mcserver import networking
from mcserver.constants import purpurmc_base_api

#TypedDicts
class BuildCommit(TypedDict):
    author_name: str            #original: author
    author_email: str         #original: email
    commit_message: str     #original: description
    commit_hash: str            #original: hash
    commit_timestamp: int #original: timestamp

class ProjectBuild(TypedDict):
    project_name: str                                #original: project
    game_version: str                                #original: version
    build_version: int                             #original: build
    build_status: str                                #original: result
    build_timestamp: int                         #original: timestamp
    build_duration: int                            #original: duration
    build_commits: list[BuildCommit] #original: commits
    metadata: dict                                     #original: metadata
    artifact_md5: str                                #original: md5

#Functions
def get_project_build(project_name: str, game_version: str, build_version: int | Literal["latest"]) -> ProjectBuild:
    response = networking.request(f"{purpurmc_base_api}/v2/{project_name}/{game_version}/{build_version}")
    response_data = json.loads(response["text"])
    
    build_commits = []
    for commit in response_data["commits"]:
        build_commits.append({
            "author_name": commit["author"],
            "author_email": commit["email"],
            "commit_message": commit["description"],
            "commit_hash": commit["hash"],
            "commit_timestamp": commit["timestamp"]
        })

    return {
        "project_name": response_data["project"],
        "game_version": response_data["version"],
        "build_version": response_data["build"],
        "build_status": response_data["result"],
        "build_timestamp": response_data["timestamp"],
        "build_duration": response_data["duration"],
        "build_commits": build_commits,
        "metadata": response_data["metadata"],
        "artifact_md5": response_data["md5"]
    }

def get_latest_project_build(project_name: str, game_version: str) -> ProjectBuild:
    return get_project_build(project_name, game_version, "latest")

def download_url(project_name: str, game_version: str, build_version: int | Literal["latest"]) -> str:
    return f"{purpurmc_base_api}/v2/{project_name}/{game_version}/{build_version}/download"

def latest_download_url(project_name: str, game_version: str) -> str:
    return download_url(project_name, game_version, "latest")
