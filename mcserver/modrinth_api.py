#Modules
# Standard
import json
from typing import Literal, TypedDict, NotRequired

# MCServer
from constants import modrinth_base_api
from networking import request
from shared import pluralize

#TypedDict
# Project Version
class ProjectVersionDependency(TypedDict):
  project_id: str | None
  dependency_type: Literal["incompatible", "required", "optional", "embedded"]
  version_id: str | None
  filename: str | None

class ProjectVersionFileHashes(TypedDict):
  sha512: str
  sha1: str

class ProjectVersionFile(TypedDict):
  url: str
  filename: str
  hashes: ProjectVersionFileHashes
  file_size: int
  file_type: str | None

class ProjectVersion(TypedDict):
  version_name: str
  version_number: str
  changelog: NotRequired[str | None]
  dependencies: list[ProjectVersionDependency]
  game_versions: list[str]
  version_type: str
  loader_names: list[str]
  featured: bool
  version_status: str
  requested_status: str | None
  version_id: str
  project_id: str
  author_id: str
  date_published: str
  download_count: int
  files: list[ProjectVersionFile]
  primary_file: ProjectVersionFile

#Errors
class NoProjectVersionFileError(Exception):
  def __init__(self, message: str, project_id: str, loader_names: list[str] | None , game_versions: list[str] | None):
    super().__init__(message)

    self.project_id = project_id
    self.loader_names = loader_names
    self.game_versions = game_versions

class NoProjectVersionError(Exception):
  def __init__(self, message: str, project_id: str, loader_names: list[str] | None , game_versions: list[str] | None):
    super().__init__(message)

    self.project_id = project_id
    self.loader_names = loader_names
    self.game_versions = game_versions

#Functions
def get_project_versions(project_id: str, game_versions: list[str] | str | None = None, loader_names: list[str] | str | None = None, include_changelog: bool = False) -> list[ProjectVersion]:
  if isinstance(game_versions, str): game_versions = [game_versions]
  if isinstance(loader_names, str): loader_names = [loader_names]

  # NOTE: 'featured' query is currently not being used because its behavior cannot be determined for now
  # function parameter that is related: featured_only: bool = False (before include_changelog and after loader_names)

  query_parameters = {
    "loaders": json.dumps(loader_names),
    "game_versions": json.dumps(game_versions),
    #"featured": json.dumps(featured_only),
    "include_changelog": json.dumps(include_changelog)
  }

  fetched_versions = json.loads(request(f"{modrinth_base_api}/v2/project/{project_id}/version", query=query_parameters)["body"])

  if len(fetched_versions) == 0:
    error_message = f"Project '{project_id}' has no version"

    if loader_names:
      error_message += f" for {pluralize('loader', len(loader_names))} '{(', '.join(loader_names)).title()}'"

    version_list = ""
    if game_versions:
      version_list = f"Minecraft {pluralize('version', len(game_versions))} '{', '.join(game_versions)}'"

      if loader_names:
        error_message += f", {version_list}"
      else:
        error_message += version_list

    raise NoProjectVersionError(error_message, project_id, loader_names, game_versions)

  project_versions = []
  for version in fetched_versions:
    # Dependency converter
    dependencies = []
    for dependency in version["dependencies"]:
      dependencies.append({
        "project_id": dependency["project_id"],
        "dependency_type": dependency["dependency_type"],
        "version_id": dependency["version_id"],
        "filename": dependency["file_name"]
      })

    # File filter
    files = []
    primary_file = {}

    for file in version["files"]:
      file_data = {
        "url": file["url"],
        "filename": file["filename"],
        "hashes": file["hashes"],
        "file_size": file["size"],
        "file_type": file["file_type"],
      }

      if file["primary"]:
        primary_file = file_data
      else:
        files.append(file_data)

    if not primary_file:
      if len(files) > 0:
        primary_file = files[0]
      else:
        raise NoProjectVersionFileError(f"Project version '{version["id"]}' has no file", version["project_id"], loader_names, game_versions)

    # Reconstruction
    project_versions.append({
      "version_name": version["name"],
      "version_number": version["version_number"],
      "changelog": version.get("changelog"),
      "dependencies": dependencies,
      "game_versions": version["game_versions"],
      "version_type": version["version_type"],
      "loader_names": version["loaders"],
      "featured": version["featured"],
      "version_status": version["status"],
      "requested_status": version["requested_status"],
      "version_id": version["id"],
      "project_id": version["project_id"],
      "author_id": version["author_id"],
      "date_published": version["date_published"],
      "download_count": version["downloads"],
      "files": files,
      "primary_file": primary_file
    })

  return project_versions
