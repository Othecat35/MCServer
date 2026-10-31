import logging
from argparse import Namespace

from .. import config, paths, shared
from ..modrinth import apis as modrinth_apis
from ..modrinth import project_records, slug_index
from ..resolver import (
    Dependency,
    human_to_resolver,
    required_only,
    resolve_dependencies,
)

logger = logging.getLogger(__name__)

def add(args: Namespace) -> int:
    projects: list[str] = args.projects

    if not (paths.configs_dir / "server.json").exists():
        logger.error("Configuration file for server does not exist, is server initialized?")

    server_config = config.read_config("server", shared.default_configs["server"]["format_version"])
    game_version = server_config["game_version"]
    loader_name = server_config["loader"]["name"]

    if loader_name == "vanilla":
        logger.error("Vanilla does not support mod or plugin.")
        return 1

    project_ids: list[str] = []
    for project in projects:
        modrinth_apis.get_project_versions(project, loader_name, game_version)

    def get_dependencies(project_id: str) -> dict[str, int]:
        dependencies: list[Dependency] = []
        if project_records.record_exists(project_id):
            project_record = project_records.read_record(project_id)
            for dependency_id, dependency_type in project_record["dependencies"].items():
                dependencies.append({
                    "project_id": dependency_id,
                    "dependency_type": dependency_type
                })

        else:
            project_version = modrinth_apis.get_project_versions(
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

    resolved_dependencies = resolve_dependencies(projects, get_dependencies, required_only)
    print(resolved_dependencies)
    return 0

    # # from ..modrinth.apis import get_project_versions

    # def get_project_versions(
    #     project_id, loader_names, game_versions, featured=None, include_changelog=True
    # ):
    #     project_version = {
    #         "embeddium": {
    #             "dependencies": [
    #                 {"project_id": "AANobbMI", "dependency_type": "incompatible"}
    #             ],
    #             "project_id": "sk9rgfiA",
    #         },
    #         "fabric-api": {"dependencies": [], "project_id": "P7dR8mSH"},
    #         "jade": {
    #             "dependencies": [
    #                 {"project_id": "AANobbMI", "dependency_type": "required"},
    #                 {"project_id": "u6dRKJwZ", "dependency_type": "optional"},
    #             ],
    #             "project_id": "nvQzSEkH",
    #         },
    #         "jei": {"dependencies": [], "project_id": "u6dRKJwZ"},
    #         "just-enough-resources-jer": {
    #             "dependencies": [
    #                 {"project_id": "u6dRKJwZ", "dependency_type": "required"}
    #             ],
    #             "project_id": "uEfK2CXF",
    #         },
    #         "origins": {
    #             "dependencies": [
    #                 {"project_id": "P7dR8mSH", "dependency_type": "required"}
    #             ],
    #             "project_id": "3BeIrqZR",
    #         },
    #         "pehkui": {
    #             "dependencies": [
    #                 {"project_id": "P7dR8mSH", "dependency_type": "required"}
    #             ],
    #             "project_id": "t5W7Jfwy",
    #         },
    #         "podium": {
    #             "dependencies": [
    #                 {"project_id": "AANobbMI", "dependency_type": "required"}
    #             ],
    #             "project_id": "fW8woQj4",
    #         },
    #         "sodium": {"dependencies": [], "project_id": "AANobbMI"},
    #         "thdilos-fox-origin-expanded": {
    #             "dependencies": [
    #                 {"project_id": "9qGn08Dr", "dependency_type": "required"},
    #                 {"project_id": "3BeIrqZR", "dependency_type": "required"},
    #                 {"project_id": "t5W7Jfwy", "dependency_type": "required"},
    #             ],
    #             "project_id": "CbsRGXBx",
    #         },
    #         "thdilos-fox-origin": {
    #             "dependencies": [
    #                 {"project_id": "3BeIrqZR", "dependency_type": "required"},
    #                 {"project_id": "t5W7Jfwy", "dependency_type": "required"},
    #             ],
    #             "project_id": "9qGn08Dr",
    #         },
    #     }

    #     id_slug = {
    #         "3BeIrqZR": "origins",
    #         "9qGn08Dr": "thdilos-fox-origin",
    #         "AANobbMI": "sodium",
    #         "CbsRGXBx": "thdilos-fox-origin-expanded",
    #         "P7dR8mSH": "fabric-api",
    #         "fW8woQj4": "podium",
    #         "nvQzSEkH": "jade",
    #         "sk9rgfiA": "embeddium",
    #         "t5W7Jfwy": "pehkui",
    #         "u6dRKJwZ": "jei",
    #         "uEfK2CXF": "just-enough-resources-jer",
    #     }

    #     a = [
    #         (
    #             project_version[project_id]
    #             if project_id in project_version
    #             else project_version[id_slug[project_id]]
    #         )
    #     ]
    #     return a


    # server_config = config.read_config(
    #     "server", shared.default_configs["server"]["format_version"]
    # )
    # loader_name = server_config["loader"]["name"]
    # game_version = server_config["game_version"]

    # cached_project_versions = {}
    # project_ids = []

    # for project in projects:
    #     project_version = get_project_versions(
    #         project, loader_name, game_version, include_changelog=False
    #     )[0]

    #     cached_project_versions[project_version["project_id"]] = project_version
    #     project_ids.append(project_version["project_id"])

    # id_to_slug: dict[str, str] = {}

    # def get_dependencies(project_id: str) -> dict[str, int]:
    #     dependencies: list[Dependency] = []

    #     # Get the latest version
    #     project_version = get_project_versions(
    #         project_id, loader_name, game_version, include_changelog=False
    #     )[0]
    #     if "dependencies" in project_version:
    #         project_dependencies = project_version["dependencies"]
    #         for dependency in project_dependencies:
    #             if not "project_id" in dependency:
    #                 continue

    #             if dependency["project_id"] is None:
    #                 continue

    #             dependencies.append(
    #                 {
    #                     "project_id": dependency["project_id"],
    #                     "dependency_type": dependency["dependency_type"],
    #                 }
    #             )

    #     return human_to_resolver(dependencies)

    # def required_only(dependency_type: int) -> bool:
    #     return dependency_type == 2

    # resolved_projects = resolver_to_human(
    #         resolve_dependencies(project_ids, get_dependencies, required_only)
    #     )

    # print(json.dumps(resolved_projects, indent=2))

    # required_projects: set[str] = set()
    # optional_projects: set[str] = set()
    # incompatible_projects: set[str] = set()

    # for project in resolved_projects:
    #     for dependent in project["dependents"]:
    #         match dependent["dependency_type"]:
    #             case "required":
    #                 required_projects.add(project["project_id"])
    #             case "optional":
    #                 optional_projects.add(project["project_id"])
    #             case "incompatible":
    #                 incompatible_projects.add(project["project_id"])

    # conflicting_projects: set[str] = required_projects & incompatible_projects

    # if conflicting_projects:
    #     print(f"I think we have conflicting project -_-, like {conflicting_projects} are in required and incompatible")

    # print(required_projects, optional_projects, incompatible_projects, conflicting_projects)

    # return 0
