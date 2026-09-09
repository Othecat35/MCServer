from argparse import Namespace


def main(args: Namespace) -> int:
    projects: list[str] = args.projects
    import logging as log

    from ..resolver import human_to_resolver, resolve_dependencies, resolver_to_human

    return 0
