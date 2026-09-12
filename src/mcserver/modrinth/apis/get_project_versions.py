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
    from ... import networking
    from ...constants import modrinth_api_url

    if loader_names is None:
        loader_names = []

    if game_versions is None:
        game_versions = []

    query_parameters = {
        "loaders": loader_names,
        "game_versions": game_versions,
        "include_changelog": include_changelog,
    }

    if featured is not None:
        query_parameters["featured"] = featured

    response = networking.request(f"{modrinth_api_url}/v2/project/{project_id}/version", query=query_parameters)
    response_json = json.loads(response["text"])
    return response_json