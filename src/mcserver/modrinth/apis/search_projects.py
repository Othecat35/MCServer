from typing import Literal


def main(
    search_query: str = "",
    search_facets: list[list[str] | str] | None = None,
    sort_index: Literal[
        "relevance", "downloads", "follows", "newest", "updated"
    ] = "relevance",
    search_offset: int = 0,
    result_limit: int = 10,
):
    """Search projects

    Args:
        search_query: The query to search for
        search_facets: Facets are an essential concept for understanding how to filter out results.
        sort_index: The sorting method used for sorting search results
        search_offset: The offset into the search. Skips this number of results
        result_limit: The number of results returned by the search (must less than 100)

    Raises:
        ValueError: sort_index has invalid option or result_limit is over 100
    """
    if search_facets is None:
        search_facets = []

    if sort_index not in ["relevance", "downloads", "follows", "newest", "updated"]:
        raise ValueError(f"Invalid sort index: {sort_index}")

    if result_limit > 100:
        raise ValueError("'result_limit' cannot be more than 100")
