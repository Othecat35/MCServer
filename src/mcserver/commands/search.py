import logging
import math
from argparse import Namespace

from mcserver import paths

from .. import config
from ..modrinth import apis as modrinth_apis
from ..modrinth.shared import SearchSortIndex
from ..shared import (
    default_configs,
    format_number,
    get_loader_context,
    pluralize,
    project_environment_name,
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
        modrinth_default_config = default_configs["modrinth"]
        modrinth_config_path = paths.configs_dir / "modrinth.json"

        if search_limit is None:
            search_limit = modrinth_default_config["config_data"]["search_limit"]
            logger.debug(
                f"search_limit is set to default modrinth configuration: {search_limit}"
            )

        if sort_index is None:
            sort_index = modrinth_default_config["config_data"]["sort_index"]
            logger.debug(
                f"sort_index is set to default modrinth configuration: {sort_index}"
            )

        if modrinth_config_path.exists():
            modrinth_config = config.read_config(
                "modrinth", modrinth_default_config["format_version"]
            )
            if search_limit is None and "search_limit" in modrinth_config:
                search_limit = modrinth_config["search_limit"]
                logger.debug(
                    f"search_limit is set to modrinth configuration file: {search_limit}"
                )

            if sort_index is None and "sort_index" in modrinth_config:
                sort_index = modrinth_config["sort_index"]
                logger.debug(
                    f"sort_index is set to modrinth configuration file: {sort_index}"
                )

    if game_version is None or loader_name is None:
        server_default_config = default_configs["server"]
        server_config_path = paths.configs_dir / "server.json"

        if server_config_path.exists():
            server_config = config.read_config(
                "server", server_default_config["format_version"]
            )
            if game_version is None and "game_version" in server_config:
                game_version = server_config["game_version"]
                logger.debug(
                    f"game_version is set to server configuration file: {game_version}"
                )

            if (
                loader_name is None
                and "loader" in server_config
                and "name" in server_config["loader"]
            ):
                loader_name = server_config["loader"]["name"]
                logger.debug(
                    f"loader_name is set to server configuration file: {loader_name}"
                )

    if no_version:
        game_version = None
        logger.debug("game_version is set to None because of no_version")

    if search_limit is None:
        logger.error("search_limit is None (somehow, really!)")
        return 1

    if sort_index is None:
        logger.error("sort_index is None (somehow, really!)")
        return 1

    if loader_name == "vanilla":
        logger.error("Vanilla does not support mods or plugin.")
        return 1

    project_label, _ = get_loader_context(loader_name)

    search_offset = search_limit * (page_number - 1)
    search_facets = [
        ["environment!=singleplayer_only"],
    ]

    if game_version is not None:
        search_facets.append([f"versions:{game_version}"])

    if loader_name is not None:
        search_facets.append([f"project_type:{project_label}"])
        search_facets.append([f"categories:{loader_name}"])

    # Searching for mods| with 'thdilos-fox-origin'| for| Minecraft 1.20.1,| Fabric| sorted by relevance...
    # Searching for plugins with 'skinsrestorer' for Minecraft 1.20.1, Paper sorted by downloads...
    # Searching for mods with 'thdilos-fox-origin' for Fabric sorted by relevance...
    # Searching for mods for Fabric sorted by relevance...
    # Searching for mods for Minecraft 1.20.1, Fabric sorted by relevance...
    # Searching for mod for Minecraft 1.20.1, Fabric sorted by relevance...
    # Wait, I don't really support datapack for now. no searching for vanilla lol

    search_info = f"Searching {pluralize(project_label, search_limit)}"
    if search_query:
        search_info += f" with '{' '.join(search_query)}'"

    search_info += " for"

    if game_version:
        search_info += f" Minecraft {game_version},"

    if loader_name:
        search_info += f" {loader_name.capitalize()}"

    search_info += f" sorted by {sort_index}..."

    logger.info(search_info)
    search_result = modrinth_apis.search_projects(
        search_query, search_facets, sort_index, search_offset, search_limit
    )

    total_hits = search_result["total_hits"]
    total_pages = math.ceil(total_hits / search_limit)

    search_hits = search_result["search_hits"]

    if page_number > total_pages:
        logger.error(
            f"Page number is larger than total pages of {total_pages} available"
        )
        return 1

    if search_result["total_hits"] == 0:
        logger.error(f"No {project_label} found.")
        return 1

    logger.info(
        f"Showing {len(search_hits)} {pluralize(project_label, len(search_hits))} out of {total_hits:,} {pluralize(project_label, total_hits)} (Page {page_number} out of {total_pages})"
    )

    for count, hit in enumerate(search_hits):
        slug_or_id = hit["project_slug"] if "project_slug" in hit else hit["project_id"]
        project_author = f"by {hit['author_username']}"

        environments = hit["environments"]
        readable_environments: list[str] = []
        for environment in environments:
            readable_environments.append(project_environment_name(environment))

        print(
            f"{hit['project_name']} ({slug_or_id}) {project_author}"
        )
        print(f"> Downloads: {format_number(hit['download_count'])} | Follows: {format_number(hit['follower_count'])}")
        print(
            f"> {', '.join(readable_environments)}"
        )
        print(f"> https://modrinth.com/{hit['project_type']}/{slug_or_id}")
        print(
            hit["short_description"]
        )

        if (count + 1) < len(search_hits):
            print()  # Print newline for readability

    return 0
