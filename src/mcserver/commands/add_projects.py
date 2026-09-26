from argparse import Namespace

def main(args: Namespace) -> int:
    projects: list[str] = args.projects
    import logging as log

    from ..modrinth.apis import get_project_versions
    from ..resolver import Dependency, human_to_resolver, resolve_dependencies, resolver_to_human
    from ..config import load_config

    server_config = load_config("server")
    loader_name = server_config["loader"]["name"]
    game_version = server_config["game_version"]

    def get_dependencies(project_id: str) -> dict[str, int]:
        dependencies: list[Dependency] = []

        # Get the latest version
        project_version = get_project_versions(project_id, loader_name, game_version, include_changelog=False)[0]
        if "dependencies" in project_version:
            project_dependencies = project_version["dependencies"]
            for dependency in project_dependencies:
                if not "project_id" in dependency:
                    continue
                    
                if dependency["project_id"] is None:
                    continue

                dependencies.append({
                    "project_id": dependency["project_id"],
                    "dependency_type": dependency["dependency_type"]
                })

        return human_to_resolver(dependencies)

    def required_only(dependency_type: int) -> bool:
        return dependency_type == 2

    print(resolver_to_human(resolve_dependencies(projects, get_dependencies, required_only, 2)))
    return 0
