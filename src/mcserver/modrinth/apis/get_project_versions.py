def main(
    project_id: str,
    loader_names: list[str] | str | None = None,
    game_versions: list[str] | str | None = None,
    featured: bool | None = None,
    include_changelog: bool = True,
):
    """List project's versions

    Args:
        project_id: The ID or slug of the project
        loader_names: The types of loaders to filter for
        game_versions: The game versions to filter for
        featured: Allows to filter for featured or non-featured versions only (trinary)
        include_changelog: Allows you to toggle the inclusion of the changelog field in the response. It is highly recommended to use include_changelog=false in most cases unless you specifically need the changelog for all versions.
    """
    import json

    from .typed_dicts import FileHashes, ProjectVersion, VersionDependency, VersionFile

    from ... import networking
    from ...constants import modrinth_api_url

    if isinstance(loader_names, str):
        loader_names = [loader_names]

    if isinstance(game_versions, str):
        game_versions = [game_versions]

    query_parameters = {"include_changelog": json.dumps(include_changelog)}

    if loader_names is not None:
        query_parameters["loaders"] = json.dumps(loader_names)

    if game_versions is not None:
        query_parameters["game_versions"] = json.dumps(game_versions)

    if featured is not None:
        query_parameters["featured"] = json.dumps(featured)

    response = networking.request(
        f"{modrinth_api_url}/v2/project/{project_id}/version", query=query_parameters
    )
    response_json = json.loads(response["text"])

    project_versions: list[ProjectVersion] = []
    for version in response_json:
        dependencies: list[VersionDependency] = []
        if "dependencies" in version:
            for dependency in version["dependencies"]:
                version_dependency: VersionDependency = {
                    "dependency_type": dependency["dependency_type"]
                }

                if "version_id" in dependency:
                    version_dependency["version_id"] = dependency["version_id"]
                if "project_id" in dependency:
                    version_dependency["project_id"] = dependency["project_id"]
                if "file_name" in dependency:
                    version_dependency["filename"] = dependency["file_name"]
                dependencies.append(version_dependency)

        files: list[VersionFile] = []
        for file in version["files"]:
            # Overcomplicate now because yes
            file_hashes: FileHashes = {}
            for hash_algorithm, hash_value in file["hashes"].items():
                if hash_algorithm in ["sha512", "sha1"]:
                    file_hashes[hash_algorithm] = hash_value

            version_file: VersionFile = {
                "file_hashes": file_hashes,
                "download_url": file["url"],
                "filename": file["filename"],
                "is_primary": file["primary"],
                "file_size": file["size"],
            }

            if "file_type" in file:
                version_file["file_type"] = file["file_type"]

            if "id" in file:
                version_file["file_id"] = file["id"]

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
