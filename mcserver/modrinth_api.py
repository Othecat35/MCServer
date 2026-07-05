#Modules
# Standard
import json
from typing import Literal, TypedDict, NotRequired

# MCServer
import networking, shared

from constants import modrinth_base_api

#Errors
#idk if I will do custom error or not
# class NoProjectVersionFileError(Exception):
#   def __init__(self, message: str, project_id: str, loader_names: list[str] | None , game_versions: list[str] | None):
#     super().__init__(message)

#     self.project_id = project_id
#     self.loader_names = loader_names
#     self.game_versions = game_versions

# class NoProjectVersionError(Exception):
#   def __init__(self, message: str, project_id: str, loader_names: list[str] | None , game_versions: list[str] | None):
#     super().__init__(message)

#     self.project_id = project_id
#     self.loader_names = loader_names
#     self.game_versions = game_versions

#TypedDict
class FileHash(TypedDict):
  sha512: NotRequired[str]
  sha1: NotRequired[str]

class VersionFile(TypedDict):
  file_hash: FileHash
  download_url: str
  filename: str
  is_primary: bool
  file_size: int
  file_type: NotRequired[Literal["required-resource-pack", "optional-resource-pack", "sources-jar", "dev-jar", "javadoc-jar", "unknown", "signature"] | None]

class VersionDependency(TypedDict):
  version_id: NotRequired[str | None]
  project_id: NotRequired[str | None]
  filename: NotRequired[str | None]
  dependency_type: Literal["required", "optional", "incompatible", "embedded"]

class ProjectVersion(TypedDict):
  version_name: NotRequired[str]
  version_number: NotRequired[str]
  changelog: NotRequired[str | None]
  dependencies: NotRequired[list[VersionDependency]]
  game_versions: NotRequired[list[str]]
  version_type: NotRequired[Literal["release", "beta", "alpha"]]
  loader_names: NotRequired[list[str]]
  is_featured: NotRequired[bool]
  status: NotRequired[Literal["listed", "archived", "draft", "unlisted", "scheduled", "unknown"]]
  requested_status: NotRequired[Literal["listed", "archived", "draft", "unlisted"] | None]
  version_id: str
  project_id: str
  author_id: str
  published_time: str
  download_count: int
  changelog_url: NotRequired[str | None]
  files: list[VersionFile]

#Functions
def get_project_versions(project_id: str, loader_names: list[str] | str | None = None, game_versions: list[str] | str | None = None, featured: bool | None = None, include_changelog: bool = True) -> list[ProjectVersion]:
  if isinstance(loader_names, str): loader_names = [loader_names]
  if isinstance(game_versions, str): game_versions = [game_versions]

  query_parameter = {
    "loaders": json.dumps(loader_names),
    "game_versions": json.dumps(game_versions),
    "include_changelog": json.dumps(include_changelog)
  }

  if featured is not None: query_parameter["featured"] = json.dumps(featured)
  response = networking.request(f"{modrinth_base_api}/v2/project/{project_id}/version", query=query_parameter)
  response_data = json.loads(response["body"])

  project_versions = []
  for version in response_data:
    dependencies = []
    if "dependencies" in version:
      for dependency in version["dependencies"]:
        version_dependency = {
          "dependency_type": dependency["dependency_type"]
        }

        if "version_id" in dependency: version_dependency["version_id"] = dependency["version_id"]
        if "project_id" in dependency: version_dependency["project_id"] = dependency["project_id"]
        if "file_name" in dependency: version_dependency["filename"] = dependency["file_name"]
        dependencies.append(version_dependency)

    files = []
    for file in version["files"]:
      #Overcomplicate now because yes
      file_hash = {}
      for hash_algorithm, hash_value in file["hashes"].items():
        if hash_algorithm in ["sha512", "sha1"]:
          file_hash[hash_algorithm] = hash_value

      version_file = {
        "file_hash": file_hash,
        "download_url": file["url"],
        "filename": file["filename"],
        "is_primary": file["primary"],
        "file_size": file["size"]
      }

      if "file_type" in file: version_file["file_type"] = file["file_type"]
      files.append(version_file)

    project_version = {
      "version_id": version["id"],
      "project_id": version["project_id"],
      "author_id": version["author_id"],
      "published_time": version["date_published"],
      "download_count": version["downloads"],
      "files": files
    }

    if "name" in version: project_version["version_name"] = version["name"]
    if "version_number" in version: project_version["version_number"] = version["version_number"]
    if "changelog" in version: project_version["changelog"] = version["changelog"]
    if "dependencies" in version: project_version["dependencies"] = dependencies
    if "game_versions" in version: project_version["game_versions"] = version["game_versions"]
    if "version_type" in version: project_version["version_type"] = version["version_type"]
    if "loaders" in version: project_version["loader_names"] = version["loaders"]
    if "featured" in version: project_version["is_featured"] = version["featured"]
    if "status" in version: project_version["status"] = version["status"]
    if "requested_status" in version: project_version["requested_status"] = version["requested_status"]
    if "changelog_url" in version: project_version["changelog_url"] = version["changelog_url"]
    project_versions.append(project_version)

  return project_versions

def get_versions_from_hashes(file_hashes: list[str] | str, hash_algorithm: Literal["sha1", "sha512"]) -> dict[str, ProjectVersion]:
  if isinstance(file_hashes, str): file_hashes = [file_hashes]

  request_body = json.dumps({
    "hashes": file_hashes,
    "algorithm": hash_algorithm
  }).encode("utf-8")

  response = networking.request(f"{modrinth_base_api}/v2/version_files", data=request_body, headers={
    "Content-Type": "application/json"
  }, method="POST")

  response_data = json.loads(response["body"])

  if len(response_data) == 0:
    raise Exception(f"No version found for {shared.pluralize('hash', len(file_hashes))} '{'\', \''.join(file_hashes)}' with algorithm '{hash_algorithm}'")

  hash_to_version = {} #originally named hash_version but I want to avoid further confusion
  for hash_value, version in response_data.items():
    dependencies = []
    if "dependencies" in version:
      for dependency in version["dependencies"]:
        version_dependency = {
          "dependency_type": dependency["dependency_type"]
        }

        if "version_id" in dependency: version_dependency["version_id"] = dependency["version_id"]
        if "project_id" in dependency: version_dependency["project_id"] = dependency["project_id"]
        if "file_name" in dependency: version_dependency["filename"] = dependency["file_name"]
        dependencies.append(version_dependency)

    files = []
    for file in version["files"]:
      #Overcomplicate now because yes
      file_hash = {}
      for hash_algorithm, file_hash_value in file["hashes"].items():
        if hash_algorithm in ["sha512", "sha1"]:
          file_hash[hash_algorithm] = file_hash_value

      version_file = {
        "file_hash": file_hash,
        "download_url": file["url"],
        "filename": file["filename"],
        "is_primary": file["primary"],
        "file_size": file["size"]
      }

      if "file_type" in file: version_file["file_type"] = file["file_type"]
      files.append(version_file)

    project_version = {
      "version_id": version["id"],
      "project_id": version["project_id"],
      "author_id": version["author_id"],
      "published_time": version["date_published"],
      "download_count": version["downloads"],
      "files": files
    }

    if "name" in version: project_version["version_name"] = version["name"]
    if "version_number" in version: project_version["version_number"] = version["version_number"]
    if "changelog" in version: project_version["changelog"] = version["changelog"]
    if "dependencies" in version: project_version["dependencies"] = dependencies
    if "game_versions" in version: project_version["game_versions"] = version["game_versions"]
    if "version_type" in version: project_version["version_type"] = version["version_type"]
    if "loaders" in version: project_version["loader_names"] = version["loaders"]
    if "featured" in version: project_version["is_featured"] = version["featured"]
    if "status" in version: project_version["status"] = version["status"]
    if "requested_status" in version: project_version["requested_status"] = version["requested_status"]
    if "changelog_url" in version: project_version["changelog_url"] = version["changelog_url"]
    hash_to_version[hash_value] = project_version

  return hash_to_version