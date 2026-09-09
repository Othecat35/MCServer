from typing import Literal


def main(
    search_query: str = "",
    search_facets: str = "",
    sort_index: Literal["relevance", "downloads", "follows", "newest", "updated"] = "relevance",
    search_offset: int = 0,
    result_limit: int = 10
):
    """Search projects

    Args:
        search_query: The query to search for
        search_facets: Facets are an essential concept for understanding how to filter out results.
        sort_index: The sorting method used for sorting search results
        search_offset: The offset into the search. Skips this number of results
        result_limit: The number of results returned by the search (must less than 100)
    """
    if result_limit > 100:
        raise ValueError("'result_limit' cannot be more than 100")
