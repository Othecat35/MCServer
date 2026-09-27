from argparse import Namespace


def main(args: Namespace) -> int:
    projects: list[str] = args.projects
    import logging as log

    # from ..modrinth.apis import get_project_versions
    from ..resolver import (
        Dependency,
        human_to_resolver,
        resolve_dependencies,
        resolver_to_human,
    )
    from ..config import load_config

    def get_project_versions(
        project_id, loader_names, game_versions, featured=None, include_changelog=True
    ):
        project_version = {
            "embeddium": {
                "dependencies": [
                    {"project_id": "AANobbMI", "dependency_type": "incompatible"}
                ],
                "project_id": "sk9rgfiA",
            },
            "fabric-api": {"dependencies": [], "project_id": "P7dR8mSH"},
            "jade": {
                "dependencies": [
                    {"project_id": "AANobbMI", "dependency_type": "required"},
                    {"project_id": "u6dRKJwZ", "dependency_type": "optional"},
                ],
                "project_id": "nvQzSEkH",
            },
            "jei": {"dependencies": [], "project_id": "u6dRKJwZ"},
            "just-enough-resources-jer": {
                "dependencies": [
                    {"project_id": "u6dRKJwZ", "dependency_type": "required"}
                ],
                "project_id": "uEfK2CXF",
            },
            "origins": {
                "dependencies": [
                    {"project_id": "P7dR8mSH", "dependency_type": "required"}
                ],
                "project_id": "3BeIrqZR",
            },
            "pehkui": {
                "dependencies": [
                    {"project_id": "P7dR8mSH", "dependency_type": "required"}
                ],
                "project_id": "t5W7Jfwy",
            },
            "podium": {
                "dependencies": [
                    {"project_id": "AANobbMI", "dependency_type": "required"}
                ],
                "project_id": "fW8woQj4",
            },
            "sodium": {"dependencies": [], "project_id": "AANobbMI"},
            "thdilos-fox-origin-expanded": {
                "dependencies": [
                    {"project_id": "9qGn08Dr", "dependency_type": "required"},
                    {"project_id": "3BeIrqZR", "dependency_type": "required"},
                    {"project_id": "t5W7Jfwy", "dependency_type": "required"},
                ],
                "project_id": "CbsRGXBx",
            },
            "thdilos-fox-origin": {
                "dependencies": [
                    {"project_id": "3BeIrqZR", "dependency_type": "required"},
                    {"project_id": "t5W7Jfwy", "dependency_type": "required"},
                ],
                "project_id": "9qGn08Dr",
            },
        }

        id_slug = {
            "3BeIrqZR": "origins",
            "9qGn08Dr": "thdilos-fox-origin",
            "AANobbMI": "sodium",
            "CbsRGXBx": "thdilos-fox-origin-expanded",
            "P7dR8mSH": "fabric-api",
            "fW8woQj4": "podium",
            "nvQzSEkH": "jade",
            "sk9rgfiA": "embeddium",
            "t5W7Jfwy": "pehkui",
            "u6dRKJwZ": "jei",
            "uEfK2CXF": "just-enough-resources-jer",
        }

        a = [
            (
                project_version[project_id]
                if project_id in project_version
                else project_version[id_slug[project_id]]
            )
        ]
        print(a)
        return a

    server_config = load_config("server")
    loader_name = server_config["loader"]["name"]
    game_version = server_config["game_version"]

    def get_dependencies(project_id: str) -> dict[str, int]:
        dependencies: list[Dependency] = []

        # Get the latest version
        project_version = get_project_versions(
            project_id, loader_name, game_version, include_changelog=False
        )[0]
        if "dependencies" in project_version:
            project_dependencies = project_version["dependencies"]
            for dependency in project_dependencies:
                if not "project_id" in dependency:
                    continue

                if dependency["project_id"] is None:
                    continue

                dependencies.append(
                    {
                        "project_id": dependency["project_id"],
                        "dependency_type": dependency["dependency_type"],
                    }
                )

        return human_to_resolver(dependencies)

    def required_only(dependency_type: int) -> bool:
        return dependency_type == 2

    print(
        resolver_to_human(
            resolve_dependencies(projects, get_dependencies, required_only, 2)
        )
    )
    return 0
