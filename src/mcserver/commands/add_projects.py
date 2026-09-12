from argparse import Namespace


def main(args: Namespace) -> int:
    projects: list[str] = args.projects
    import logging as log

    from ..modrinth.apis import get_project_versions
    from ..resolver import human_to_resolver, resolve_dependencies, resolver_to_human

    print(get_project_versions(projects[0], include_changelog=False))
    return 0
