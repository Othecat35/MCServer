#Modules
# Standard
import json
from typing import Literal, NotRequired, TypedDict

# MCServer
from .. import networking
from ..constants import modrinth_base_api

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

class DonationPlatform(TypedDict):
    platform_id: NotRequired[str]
    platform_name: NotRequired[str]
    dnation_url: NotRequired[str]

class ModeratorMessage(TypedDict):
    message: str
    body: str

class ProjectLicense(TypedDict):
    license_id: NotRequired[str]
    license_name: NotRequired[str]
    license_url: NotRequired[str | None]

class GalleryImage(TypedDict):
    image_url: str
    is_featured: bool
    image_title: NotRequired[str | None]
    image_description: NotRequired[str | None]
    created_time: str
    image_index: NotRequired[int]

class Project(TypedDict):
    project_slug: NotRequired[str]
    project_title: NotRequired[str]
    summary: NotRequired[str]
    categories: NotRequired[list[str]]
    client_side: NotRequired[Literal["required", "optional", "unsupported", "unknown"]]
    server_side: NotRequired[Literal["required", "optional", "unsupported", "unknown"]]
    description: NotRequired[str]
    status: NotRequired[Literal["approved", "archived", "rejected", "draft", "unlisted", "processing", "withheld", "scheduled", "private", "unknown"]]
    requested_status: NotRequired[Literal["approved", "archived", "unlisted", "private", "draft"] | None]
    additional_categories: list[str]
    issues_url: NotRequired[str | None]
    source_url: NotRequired[str | None]
    wiki_url: NotRequired[str | None]
    discord_url: NotRequired[str | None]
    donation_platforms: NotRequired[list[DonationPlatform]]
    project_type: Literal["mod", "modpack", "resourcepack", "shader"]
    download_count: int
    icon_url: NotRequired[str | None]
    icon_color: NotRequired[int | None]
    thread_id: NotRequired[str]
    monetization_status: NotRequired[Literal["monetized", "demonetized", "force-demonetized"]]
    project_id: str
    team_id: str
    description_url: NotRequired[str | None]
    moderator_message: NotRequired[ModeratorMessage]
    published_time: NotRequired[str]
    last_updated_time: NotRequired[str]
    approved_time: NotRequired[str]
    queued_time: NotRequired[str]
    follower_count: int
    license: NotRequired[ProjectLicense]
    version_ids: NotRequired[list[str]]
    game_versions: NotRequired[list[str]]
    loader_names: NotRequired[list[str]]
    image_gallery: list[GalleryImage]

#Functions
def get_project_versions(project_id: str, loader_names: list[str] | str | None = None, game_versions: list[str] | str | None = None, featured: bool | None = None, include_changelog: bool = True) -> list[ProjectVersion]:
    if isinstance(loader_names, str): loader_names = [loader_names]
    if isinstance(game_versions, str): game_versions = [game_versions]

    query_parameter = {
        "loaders": json.dumps(loader_names),
        "game_versions": json.dumps(game_versions),
        "include_changelog": json.dumps(include_changelog)
    }

    # NOTE: 'featured' is trinary
    if featured is not None: query_parameter["featured"] = json.dumps(featured)

    response = networking.request(f"{modrinth_base_api}/v2/project/{project_id}/version", query=query_parameter)
    response_json = json.loads(response["text"])

    project_versions = []
    for version in response_json:
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

        version = {
            "version_id": version["id"],
            "project_id": version["project_id"],
            "author_id": version["author_id"],
            "published_time": version["date_published"],
            "download_count": version["downloads"],
            "files": files
        }

        if "name" in version: version["version_name"] = version["name"]
        if "version_number" in version: version["version_number"] = version["version_number"]
        if "changelog" in version: version["changelog"] = version["changelog"]
        if "dependencies" in version: version["dependencies"] = dependencies
        if "game_versions" in version: version["game_versions"] = version["game_versions"]
        if "version_type" in version: version["version_type"] = version["version_type"]
        if "loaders" in version: version["loader_names"] = version["loaders"]
        if "featured" in version: version["is_featured"] = version["featured"]
        if "status" in version: version["status"] = version["status"]
        if "requested_status" in version: version["requested_status"] = version["requested_status"]
        if "changelog_url" in version: version["changelog_url"] = version["changelog_url"]
        project_versions.append(version)

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

    response_json = json.loads(response["text"])

    hash_to_version_map = {}
    for hash_value, version in response_json.items():
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
        hash_to_version_map[hash_value] = project_version

    return hash_to_version_map

def get_projects(project_ids: list[str] | str) -> ModrinthProject:
    if isinstance(project_ids, str): project_ids = [project_ids]

    query_parameters = {
        "ids": json.dumps(project_ids)
    }

    response = networking.request(f"{modrinth_base_api}/v2/projects", query=query_parameters)
    response_json = json.loads(response["text"])

    projects
    for project in response_json:
