import json
import logging

from mcserver.modrinth.typings.search_projects import DisclosureType

from ... import networking
from ...constants import modrinth_api_url
from .. import shared
from ..shared import SearchSortIndex
from ..typings import (
    AllProjectType,
    Environment,
    EnvironmentSide,
    ProjectType,
    SearchHit,
    SearchResult,
)

logger = logging.getLogger(__name__)


class SearchProjectsError(Exception):
    pass


def search_projects(
    search_query: str | list[str] | None = None,
    search_facets: list[list[list[str] | str]] | None = None,
    sort_index: SearchSortIndex = "relevance",
    search_offset: int = 0,
    search_limit: int = 10,
) -> SearchResult:
    """Search projects

    Args:
        search_query: The query to search for
        search_facets: Facets are an essential concept for understanding how to filter out results.
        sort_index: The sorting method used for sorting search results
        search_offset: The offset into the search. Skips this number of results
        search_limit: The number of results returned by the search (must less than or equal to 100)

    Raises:
        ValueError: sort_index has invalid option or search_limit is over 100
    """
    if isinstance(search_query, list):
        search_query = " ".join(search_query)

    if search_facets is None:
        search_facets = []

    if sort_index not in ["relevance", "downloads", "follows", "newest", "updated"]:
        raise ValueError(f"Invalid sort index: {sort_index}")

    if search_limit > 100:
        raise ValueError("'search_limit' cannot be more than 100")

    query_parameters = {
        "facets": str(json.dumps(search_facets)),
        "index": sort_index,
        "offset": search_offset,
        "limit": search_limit,
    }

    if search_query is not None:
        query_parameters["query"] = search_query

    response = networking.request(
        f"{modrinth_api_url}/v2/search", query=query_parameters
    )

    # Mostly just to make pyright happy
    if "json" in response:
        response_json = response["json"]
        if isinstance(response_json, list):
            raise SearchProjectsError("Response JSON is a list")
    else:
        raise SearchProjectsError("Response is not JSON")

    search_hits: list[SearchHit] = []
    for hit in response_json["hits"]:
        project_type: ProjectType = hit["project_type"]
        if project_type not in shared.PROJECT_TYPE:
            logger.debug(f"Unknown project_type: {project_type}")

        all_project_types: list[AllProjectType] = hit["all_project_types"]
        for all_project_type in all_project_types:
            if all_project_type not in shared.ALL_PROJECT_TYPE:
                logger.debug(f"Unknown all_project_type: {all_project_type}")

        environments: list[Environment] = hit["environment"]
        for environment in environments:
            if environment not in shared.ENVIRONMENT:
                logger.debug(f"Unknown environment: {environment}")

        disclosure_types: list[DisclosureType] = hit["disclosure_types"]
        for disclosure_type in disclosure_types:
            if disclosure_type not in shared.DISCLOSURE_TYPE:
                logger.debug(f"Unknown disclosure_type: {disclosure_type}")

        client_side: EnvironmentSide = hit["client_side"]
        if client_side not in shared.ENVIRONMENT_SIDE:
            logger.warning(f"Unknown client side: {client_side}")

        server_side: EnvironmentSide = hit["server_side"]
        if server_side not in shared.ENVIRONMENT_SIDE:
            logger.warning(f"Unknown server side: {server_side}")

        search_hit: SearchHit = {
            "project_id": hit["project_id"],
            "project_type": project_type,
            "all_project_types": all_project_types,
            "project_name": hit["title"],
            "short_description": hit["description"],
            "author_username": hit["author"],
            "categories": hit["categories"],
            "display_categories": hit["display_categories"],
            "game_versions": hit["versions"],
            "download_count": hit["downloads"],
            "follower_count": hit["follows"],
            "icon_url": hit["icon_url"],
            "created_time": hit["date_created"],
            "updated_time": hit["date_modified"],
            "latest_version_id": hit["latest_version"],
            "license_id": hit["license"],
            "environments": environments,
            "disclosure_types": disclosure_types,
            "image_urls": hit["gallery"],
            "client_side": client_side,
            "server_side": server_side,
        }

        if "slug" in hit:
            search_hit["project_slug"] = hit["slug"]

        if "author_id" in hit:
            search_hit["author_id"] = hit["author_id"]

        if "organization" in hit:
            search_hit["organization_name"] = hit["organization"]

        if "organization_id" in hit:
            search_hit["organization_id"] = hit["organization_id"]

        if "featured_gallery" in hit:
            search_hit["featured_gallery"] = hit["featured_gallery"]

        if "color" in hit:
            search_hit["icon_color"] = hit["color"]

        search_hits.append(search_hit)

    search_result: SearchResult = {
        "search_hits": search_hits,
        "result_offset": response_json["offset"],
        "result_limit": response_json["limit"],
        "total_hits": response_json["total_hits"],
    }

    return search_result
