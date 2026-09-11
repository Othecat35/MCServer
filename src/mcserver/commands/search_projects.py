from argparse import Namespace


def main(args: Namespace) -> int:
    query: list[str] = args.query
    import logging as log
    from ..modrinth.apis import search_projects

    print(search_projects("better", search_facets=[["environment:dedicated_server_only"]], result_limit=1000))
    return 1
