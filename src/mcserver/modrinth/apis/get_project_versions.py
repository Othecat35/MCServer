from ..typings import ProjectVersion


class GetProjectVersionsError(Exception):
    pass


def get_project_versions(
    project_id: str,
    loader_names: list[str] | str | None = None,
    game_versions: list[str] | str | None = None,
    featured: bool | None = None,
    include_changelog: bool = True,
) -> list[ProjectVersion]:
    """List project's versions

    Args:
        project_id: The ID or slug of the project
        loader_names: The types of loaders to filter for
        game_versions: The game versions to filter for
        featured: Allows to filter for featured or non-featured versions only (trinary)
        include_changelog: Allows you to toggle the inclusion of the changelog field in the response. It is highly recommended to use include_changelog=false in most cases unless you specifically need the changelog for all versions.
    """
    if isinstance(loader_names, str):
        loader_names = [loader_names]

    if isinstance(game_versions, str):
        game_versions = [game_versions]

    import json
    import logging

    from ... import networking
    from .. import constants, shared
    from ..typings import (
        Dependency,
        File,
        FileHashes,
        FileType,
        RequestedVersionStatus,
        VersionStatus,
        VersionType,
    )

    logger = logging.getLogger(__name__)

    query_parameters = {"include_changelog": json.dumps(include_changelog)}

    if loader_names is not None:
        query_parameters["loaders"] = json.dumps(loader_names)

    if game_versions is not None:
        query_parameters["game_versions"] = json.dumps(game_versions)

    if featured is not None:
        query_parameters["featured"] = json.dumps(featured)

    response = networking.request(
        f"{constants.modrinth_api_url}/v2/project/{project_id}/version",
        query=query_parameters,
    )

    if "json" not in response:
        raise GetProjectVersionsError("Cannot load JSON response")

    project_versions: list[ProjectVersion] = []
    for version in response["json"]:
        dependencies: list[Dependency] = []
        for dependency in version.get("dependencies", []):
            version_dependency: Dependency = {
                "dependency_type": dependency["dependency_type"]
            }

            if "version_id" in dependency:
                version_dependency["version_id"] = dependency["version_id"]

            if "project_id" in dependency:
                version_dependency["project_id"] = dependency["project_id"]

            if "file_name" in dependency:
                version_dependency["file_name"] = dependency["file_name"]

            dependencies.append(version_dependency)

        files: list[File] = []
        for file in version["files"]:
            file_type: FileType = file["file_type"]
            if file_type not in shared.FILE_TYPE:
                logger.debug(f"Unknown file type: {file_type}")

            version_file_hashes: FileHashes = {}
            file_hashes = file["hashes"]
            if "sha512" in file["hashes"]:
                version_file_hashes["sha512"] = file_hashes["sha512"]

            if "sha1" in file["hashes"]:
                version_file_hashes["sha1"] = file_hashes["sha1"]

            version_file: File = {
                "file_hashes": file_hashes,
                "download_url": file["url"],
                "file_name": file["filename"],
                "is_primary": file["primary"],
                "file_size": file["size"],
            }

            if "file_type" in file:
                version_file["file_type"] = file["file_type"]

            files.append(version_file)

        project_version: ProjectVersion = {
            "version_id": version["id"],
            "project_id": version["project_id"],
            "author_id": version["author_id"],
            "published_time": version["date_published"],
            "download_count": version["downloads"],
            "environment": version["environment"],
            "files": files,
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
            version_type: VersionType = version["version_type"]
            if version_type not in shared.VERSION_TYPE:
                logger.debug(f"Unknown version_type: {version_type}")

            project_version["version_type"] = version_type

        if "loaders" in version:
            project_version["loader_names"] = version["loaders"]

        if "featured" in version:
            project_version["is_featured"] = version["featured"]

        if "status" in version:
            version_status: VersionStatus = version["status"]
            if version_status not in shared.VERSION_STATUS:
                logger.debug(f"Unknown version_status: {version_status}")

            project_version["version_status"] = version_status

        if "requested_status" in version:
            requested_status_version: RequestedVersionStatus = version[
                "requested_status"
            ]
            if requested_status_version not in shared.REQUESTED_VERSION_STATUS:
                logger.info(
                    f"Unknown requested_status_version: {requested_status_version}"
                )

            project_version["requested_version_status"] = requested_status_version

        if "changelog_url" in version:
            project_version["changelog_url"] = version["changelog_url"]

        project_versions.append(project_version)

    return project_versions
