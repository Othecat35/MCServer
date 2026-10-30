import logging
from argparse import Namespace

from mcserver import paths

from .. import config, shared
from ..modrinth import apis as modrinth_apis
from ..modrinth.shared import SearchSortIndex
from ..shared import (
    format_number,
    pluralize,
    project_environment_name,
    loader_context,
    set_loader_context,
)

logger = logging.getLogger(__name__)

def search(args: Namespace) -> int:
    search_query: list[str] = args.search_query
    search_limit: int | None = args.search_limit
    page_number: int = args.page_number
    sort_index: SearchSortIndex | None = args.sort_index
    game_version: str | None = args.game_version
    no_version: str = args.no_version
    loader_name: str | None = args.loader_name

    if search_limit is None or sort_index is None:
        modrinth_default_config = shared.default_configs["modrinth"]
        modrinth_config_path = paths.configs_dir / "modrinth.json"

        if search_limit is None:
            search_limit = modrinth_default_config["config_data"]["search_limit"]
            logger.debug(f"search_limit is set to default modrinth configuration: {search_limit}")

        if sort_index is None:
            sort_index = modrinth_default_config["config_data"]["sort_index"]
            logger.debug(f"sort_index is set to default modrinth configuration: {sort_index}")

        if modrinth_config_path.exists():
            modrinth_config = config.read_config("modrinth", modrinth_default_config["format_version"])
            if search_limit is None and "search_limit" in modrinth_config:
                search_limit = modrinth_config["search_limit"]
                logger.debug(f"search_limit is set to modrinth configuration file: {search_limit}")

            if sort_index is None and "sort_index" in modrinth_config:
                sort_index = modrinth_config["sort_index"]
                logger.debug(f"sort_index is set to modrinth configuration file: {sort_index}")

    if game_version is None or loader_name is None:
        server_default_config = shared.default_configs["server"]
        server_config_path = paths.configs_dir / "server.json"

        if server_config_path.exists():
            server_config = config.read_config("server", server_default_config["format_version"])
            if game_version is None and "game_version" in server_config:
                game_version = server_config["game_version"]
                logger.debug(f"game_version is set to server configuration file: {game_version}")

            if loader_name is None and "loader" in server_config and "name" in server_config["loader"]:
                loader_name = server_config["loader"]["name"]
                logger.debug(f"loader_name is set to server configuration file: {loader_name}")

    if no_version:
        game_version = None
        logger.debug("game_version is set to None because of no_version")

    if search_limit is None:
        logger.error("search_limit is None (somehow, really!)")
        return 1

    if sort_index is None:
        logger.error("sort_index is None (somehow, really!)")
        return 1

    if loader_name is None:
        logger.error("sort_index is None (somehow, really!)")
        return 1

    shared.set_loader_context(loader_name)
    if shared.loader_context["project_label"] is None:
        logger.error("project_label is None (somehow, really!)")
        return 1

    search_offset = search_limit * (page_number - 1)
    search_facets = [["environment!=singleplayer_only"]]

    if shared.loader_context["project_label"] != "project":
        search_facets.append([f"project_type:{shared.loader_context["project_label"]}"])

    if game_version is not None:
        search_facets.append([f"versions:{game_version}"])

    if loader_name is not None:
        search_facets.append([f"categories:{loader_name}"])

    search_info = f"Searching {pluralize(shared.loader_context["project_label"], search_limit)}"
    if search_query:
        search_info += f" for {' '.join(search_query)}"

    logger.info(search_info)
    #search_result = modrinth_apis.search_projects(search_query, search_facets, sort_index, search_offset, search_limit)

    for search_hit in search_result["search_hits"]:
        slug_or_id = search_hit.get("project_slug", search_hit["project_id"])
        print(f"{search_hit['project_name']} ({slug_or_id}) by {search_hit['author_username']}")

    # server_config = {}

    # if not (loader_name and game_version):
    #     try:
    #         server_config = config.read_config("server", 1)
    #     except FileNotFoundError:
    #         pass  # ignore because it doesn't really need the config. just as "personalization" per server

    # game_version = game_version or server_config.get("game_version", "")
    # loader_name = loader_name or server_config.get("loader", {}).get("name", "")

    # if no_version:
    #     game_version = ""

    # if not loader_name:
    #     loader_name = "vanilla"
    # elif loader_name != "vanilla":
    #     set_loader_context(loader_name)

    # search_offset = search_limit * (page_number - 1)

    # search_info = f"Searching {pluralize(shared.loader_context['project_label'])}"

    # if search_query:
    #     search_info += f" with '{' '.join(search_query)}'"

    # search_info += f" for {loader_name.capitalize()}"

    # if game_version:
    #     search_info += f", Minecraft {game_version}"

    # search_info += f", sorted by {sort_index}"

    # log.info(search_info + "...")
    # search_result = search_projects(
    #     search_query=search_query,
    #     sort_index=sort_index,
    #     search_limit=search_limit,
    #     search_offset=search_offset,
    # )

    # search_hits = search_result["search_hits"]
    # if len(search_hits) == 0:
    #     log.error(f"No {shared.loader_context['project_label']} found.")

    # for count, hit in enumerate(search_hits):
    #     slug_or_id = hit["project_slug"] if "project_slug" in hit else hit["project_id"]
    #     project_author = wrap_ansi(f"by {hit['author_username']}", "gray")

    #     project_environments = []
    #     if len(hit["project_environments"]) == 0:
    #         project_environments.append("No environment")
    #     else:
    #         for project_environment in hit["project_environments"]:
    #             project_environments.append(
    #                 project_environment_name(project_environment)
    #             )

    #     print(
    #         f"{wrap_ansi(hit['project_name'], 'bold')} ({slug_or_id}) {project_author}"
    #     )
    #     print(
    #         f"> {', '.join(project_environments)} | Downloads: {format_number(hit['download_count'])} | Follows: {format_number(hit['follow_count'])}"
    #     )
    #     print(f"> https://modrinth.com/{hit['project_type']}/{slug_or_id}")
    #     print(
    #         wrap_string(hit["short_description"], initial_indent=2, subsequent_indent=1)
    #     )

    #     if (count + 1) < len(search_hits):
    #         print()  # Print newline for readability

    return 0
