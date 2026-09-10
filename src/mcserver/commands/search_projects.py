from argparse import Namespace


def main(args: Namespace) -> int:
    query: list[str] = args.query
    import logging as log
    from ..modrinth.apis import search_projects

    print(search_projects())
    return 1
