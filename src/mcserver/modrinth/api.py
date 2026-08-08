#Modules
# Standard
import json
from typing import Literal, NotRequired, TypedDict

# MCServer
from .. import networking
from ..constants import modrinth_api_url

#TypedDict
# Project Version
class FileHashes(TypedDict):
    sha512: NotRequired[str]
    sha1: NotRequired[str]

class VersionFile(TypedDict):
    file_hashes: FileHashes
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
    published_time: str # Time format: ISO-8601
    download_count: int
    changelog_url: NotRequired[str | None]
    files: list[VersionFile]

# Project Information
class DonationPlatform(TypedDict):
    platform_id: NotRequired[str]
    platform_name: NotRequired[str]
    donation_url: NotRequired[str]

class ModeratorMessage(TypedDict):
    message: NotRequired[str]
    body: NotRequired[str | None]

class ProjectLicense(TypedDict):
    license_id: NotRequired[str]
    license_name: NotRequired[str]
    license_url: NotRequired[str | None]

class GalleryImage(TypedDict):
    image_url: str
    is_featured: bool
    image_title: NotRequired[str | None]
    image_description: NotRequired[str | None]
    created_time: str                          # Time format: ISO-8601
    image_order: NotRequired[int]

class ProjectInformation(TypedDict):
    project_slug: NotRequired[str]
    project_title: NotRequired[str]
    summary: NotRequired[str]
    categories: NotRequired[list[str]]
    client_side: NotRequired[Literal["required", "optional", "unsupported", "unknown"]]
    server_side: NotRequired[Literal["required", "optional", "unsupported", "unknown"]]
    description: NotRequired[str]
    status: NotRequired[Literal["approved", "archived", "rejected", "draft", "unlisted", "processing", "withheld", "scheduled", "private", "unknown"]]
    requested_status: NotRequired[Literal["approved", "archived", "unlisted", "private", "draft"] | None]
    additional_categories: NotRequired[list[str]]
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
    moderator_message: NotRequired[ModeratorMessage | None] # NOTE: The docs is misleading
    published_time: str                    # Time format: ISO-8601
    last_updated_time: str                 # Time format: ISO-8601
    approved_time: NotRequired[str | None] # Time format: ISO-8601
    queued_time: NotRequired[str | None]   # Time format: ISO-8601
    follower_count: int
    license: NotRequired[ProjectLicense]
    version_ids: NotRequired[list[str]]
    game_versions: NotRequired[list[str]]
    loader_names: NotRequired[list[str]]
    project_gallery: NotRequired[list[GalleryImage]]

class SearchHit(TypedDict):
    project_slug: NotRequired[str]
    project_title: NotRequired[str]
    short_description: NotRequired[str]
    categories: NotRequired[list[str]]
    client_side: NotRequired[Literal["required", "optional", "unsupported", "unknown"]]
    server_side: NotRequired[Literal["required", "optional", "unsupported", "unknown"]]
    project_type: Literal["mod", "modpack", "resourcepack", "shader"]
    download_count: int
    icon_url: NotRequired[str | None]
    icon_color: NotRequired[int | None]
    thread_id: NotRequired[str]
    monetization_status: NotRequired[Literal["monetized", "demonetized", "force-demonetized"]]
    project_id: str
    all_project_types: list[str]
    author_username: str
    display_categories: NotRequired[list[str]]
    game_versions: list[str]
    follower_count: int
    created_time: str  # Time Format: ISO-8601
    modified_time: str # Time Format: ISO-8601
    latest_game_version: NotRequired[str]
    license_id: str
    gallery_images: NotRequired[list[str]]
    featured_galeery: NotRequired[str | None]

class SearchResult(TypedDict):
    hits: list[SearchHit]
    offset: int
    limit: int
    total_hits: int

#Functions
def get_project_versions(project_id: str, loader_names: list[str] | str | None = None, game_versions: list[str] | str | None = None, featured: bool | None = None, include_changelog: bool = True) -> list[ProjectVersion]:
    if isinstance(loader_names, str):
        loader_names = [loader_names]

    if isinstance(game_versions, str):
        game_versions = [game_versions]

    query_parameter = {
        "loaders": json.dumps(loader_names),
        "game_versions": json.dumps(game_versions),
        "include_changelog": json.dumps(include_changelog)
    }

    # NOTE: 'featured' is trinary
    if featured is not None:
        query_parameter["featured"] = json.dumps(featured)

    response = networking.request(f"{modrinth_api_url}/v2/project/{project_id}/version", query=query_parameter)
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
            file_hashes = {}
            for hash_algorithm, hash_value in file["hashes"].items():
                if hash_algorithm in ["sha512", "sha1"]:
                    file_hashes[hash_algorithm] = hash_value

            version_file = {
                "file_hashes": file_hashes,
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

        if "name" in version:
            project_version["version_name"] = version["name"]

        if "version_number" in version:
            project_version["version_number"] = version["version_number"]

        if "changelog" in version:
            project_version["changelog"] = version["changelog"]

        if "dependencies" in version:
            project_version["dependencies"] = dependencies

        if "game_versions" in version:
            project_version["game_versions"] = version["game_versions"]

        if "version_type" in version:
            project_version["version_type"] = version["version_type"]

        if "loaders" in version:
            project_version["loader_names"] = version["loaders"]

        if "featured" in version:
            project_version["is_featured"] = version["featured"]

        if "status" in version:
            project_version["status"] = version["status"]

        if "requested_status" in version:
            project_version["requested_status"] = version["requested_status"]

        if "changelog_url" in version:
            project_version["changelog_url"] = version["changelog_url"]

        project_versions.append(project_version)

    return project_versions

def get_versions_from_hashes(file_hashes: list[str] | str, hash_algorithm: Literal["sha1", "sha512"]) -> dict[str, ProjectVersion]:
    if isinstance(file_hashes, str):
        file_hashes = [file_hashes]

    request_body = json.dumps({
        "hashes": file_hashes,
        "algorithm": hash_algorithm
    }).encode("utf-8")

    response = networking.request(f"{modrinth_api_url}/v2/version_files", data=request_body, headers={
        "Content-Type": "application/json"
    }, method="POST")

    response_json = json.loads(response["text"])

    hash_to_version = {}
    for hash_value, version in response_json.items():
        dependencies = []
        if "dependencies" in version:
            for dependency in version["dependencies"]:
                version_dependency = {
                    "dependency_type": dependency["dependency_type"]
                }

                if "version_id" in dependency:
                    version_dependency["version_id"] = dependency["version_id"]

                if "project_id" in dependency:
                    version_dependency["project_id"] = dependency["project_id"]

                if "file_name" in dependency:
                    version_dependency["filename"] = dependency["file_name"]

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

        if "name" in version:
            project_version["version_name"] = version["name"]

        if "version_number" in version:
            project_version["version_number"] = version["version_number"]

        if "changelog" in version:
            project_version["changelog"] = version["changelog"]

        if "dependencies" in version:
            project_version["dependencies"] = dependencies

        if "game_versions" in version:
            project_version["game_versions"] = version["game_versions"]

        if "version_type" in version:
            project_version["version_type"] = version["version_type"]

        if "loaders" in version:
            project_version["loader_names"] = version["loaders"]

        if "featured" in version:
            project_version["is_featured"] = version["featured"]

        if "status" in version:
            project_version["status"] = version["status"]

        if "requested_status" in version:
            project_version["requested_status"] = version["requested_status"]

        if "changelog_url" in version:
            project_version["changelog_url"] = version["changelog_url"]

        hash_to_version[hash_value] = project_version

    return hash_to_version

def get_project_information(project_ids: list[str] | str) -> list[ProjectInformation]:
    if isinstance(project_ids, str):
        project_ids = [project_ids]

    query_parameters: dict[str, str] = {
        "ids": json.dumps(project_ids)
    }

    response = networking.request(f"{modrinth_api_url}/v2/projects", query=query_parameters)
    response_json = json.loads(response["text"])

    project_informations: list[ProjectInformation] = []
    for project in response_json:
        client_side: Literal["required", "optional", "unsupported", "unknown"] = "unknown"
        if "client_side" in project:
            if project["client_side"] in ["required", "optional", "unsupported", "unknown"]:
                client_side = project["client_side"]

        server_side: Literal["required", "optional", "unsupported", "unknown"] = "unknown"
        if "server_side" in project:
            if project["server_side"] in ["required", "optional", "unsupported", "unknown"]:
                server_side = project["server_side"]

        status: Literal["approved", "archived", "rejected", "draft", "unlisted", "processing", "withheld", "scheduled", "private", "unknown"] = "unknown"
        if "status" in project:
            if project["status"] in ["approved", "archived", "rejected", "draft", "unlisted", "processing", "withheld", "scheduled", "private", "unknown"]:
                status = project["status"]

        requested_status: Literal["approved", "archived", "unlisted", "private", "draft"] | None = None
        if "requested_status" in project:
            requested_status_data = project["requested_status"]
            if requested_status_data in ["approved", "archived", "unlisted", "private", "draft"] or requested_status_data is None:
                requested_status = requested_status_data

        monetization_status: Literal["monetized", "demonetized", "force-demonetized"] = "monetized"
        if "monetization_status" in project:
            if project["monetization_status"] in ["monetized", "demonetized", "force-demonetized"]:
                monetization_status = project["monetization_status"]

        donation_platforms: list[DonationPlatform] = []
        if "donation_urls" in project:
            for platform in project["donation_urls"]:
                donation_platform: DonationPlatform = {}

                if "id" in platform: donation_platform["platform_id"] = platform["id"]
                if "platform" in platform: donation_platform["platform_name"] = platform["platform"]
                if "url" in platform: donation_platform["donation_url"] = platform["url"]
                donation_platforms.append(donation_platform)

        moderator_message: ModeratorMessage | None = None
        if "moderator_message" in project:
            moderator_message_data = project["moderator_message"]
            if moderator_message_data is None:
                moderator_message = None
            else:
                # pls forgive me I was tired, maybe you fix it then
                if moderator_message is None:
                    moderator_message = {}

                if "message" in moderator_message_data: moderator_message["message"] = moderator_message_data["message"]
                if "body" in moderator_message_data: moderator_message["body"] = moderator_message_data["body"]

        project_license: ProjectLicense = {}
        if "license" in project:
            license_data = project["license"]
            if "id" in license_data: project_license["license_id"] = license_data["id"]
            if "name" in license_data: project_license["license_name"] = license_data["name"]
            if "url" in license_data: project_license["license_url"] = license_data["url"]

        project_gallery: list[GalleryImage] = []
        if "gallery" in project:
            for image in project["gallery"]:
                gallery_image: GalleryImage = {
                    "image_url": image["url"],
                    "is_featured": image["featured"],
                    "created_time": image["created"]
                }

                if "title" in image: gallery_image["image_title"] = image["title"]
                if "description" in image: gallery_image["image_description"] = image["description"]
                if "ordering" in image: gallery_image["image_order"] = image["ordering"]
                project_gallery.append(gallery_image)

        project_information: ProjectInformation = {
            "project_type": project["project_type"],
            "download_count": project["downloads"],
            "project_id": project["id"],
            "team_id": project["team"],
            "published_time": project["published"],
            "last_updated_time": project["updated"],
            "follower_count": project["followers"]
        }

        if "slug" in project:
            project_information["project_slug"] = project["slug"]

        if "title" in project:
            project_information["project_title"] = project["title"]

        if "description" in project:
            project_information["summary"] = project["description"]

        if "categories" in project:
            project_information["categories"] = project["categories"]

        if "client_side" in project:
            project_information["client_side"] = client_side

        if "server_side" in project:
            project_information["server_side"] = server_side

        if "body" in project:
            project_information["description"] = project["body"]

        if "status" in project:
            project_information["status"] = status

        if "requested_status" in project:
            project_information["requested_status"] = requested_status

        if "additional_categories" in project:
            project_information["additional_categories"] = project["additional_categories"]

        if "issues_url" in project:
            project_information["issues_url"] = project["issues_url"]

        if "source_url" in project:
            project_information["source_url"] = project["source_url"]

        if "wiki_url" in project:
            project_information["wiki_url"] = project["wiki_url"]

        if "discord_url" in project:
            project_information["discord_url"] = project["discord_url"]

        if "donation_urls" in project:
            project_information["donation_platforms"] = donation_platforms

        if "icon_url" in project:
            project_information["icon_url"] = project["icon_url"]

        if "color" in project:
            project_information["icon_color"] = project["color"]

        if "thread_id" in project:
            project_information["thread_id"] = project["thread_id"]

        if "monetization_status" in project:
            project_information["monetization_status"] = monetization_status

        if "body_url" in project:
            project_information["description_url"] = project["body_url"]

        if "moderator_message" in project:
            project_information["moderator_message"] = moderator_message

        if "approved" in project:
            project_information["approved_time"] = project["approved"]

        if "queued" in project:
            project_information["queued_time"] = project["queued"]

        if "license" in project:
            project_information["license"] = project_license

        if "versions" in project:
            project_information["version_ids"] = project["versions"]

        if "game_versions" in project:
            project_information["game_versions"] = project["game_versions"]

        if "loaders" in project:
            project_information["loader_names"] = project["loaders"]

        if "gallery" in project:
            project_information["project_gallery"] = project_gallery

        project_informations.append(project_information)

    return project_informations

def search_projects(query: str, facets: list[list[str]], index: Literal["relevance", "downloads", "follows", "newest", "updated"] = "relevance", offset: int = 0, limit: int = 10) -> SearchResult:
    search_result: SearchResult = {}
    return search_result