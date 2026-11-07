import logging
from argparse import Namespace

from mcserver import networking

from .. import config, paths, resolver, shared
from ..modrinth import apis as modrinth_api
from ..modrinth.typings import Dependency, DependencyType, ProjectVersion

logger = logging.getLogger(__name__)


class GetDependenciesError(Exception):
    pass


class ResolverTranslationError(Exception):
    pass


dependency_types: dict[DependencyType, int] = {
    "embedded": 0,
    "optional": 1,
    "required": 2,
    "incompatible": 3,
}


def human_to_resolver(dependencies: list[Dependency]) -> dict[str, int]:
    resolver_dependencies: dict[str, int] = {}
    for dependency in dependencies:
        if "project_id" not in dependency:
            raise ResolverTranslationError("'project_id' does not exist in dependency")

        dependency_id = dependency["project_id"]
        if dependency_id is None:
            raise ResolverTranslationError("'project_id' is None")

        if dependency["dependency_type"] == "embedded":
            logger.debug("Skipping 'embedded' dependency")
            continue

        resolver_dependencies[dependency_id] = dependency_types[
            dependency["dependency_type"]
        ]

    return resolver_dependencies


def run(args: Namespace) -> int:
    projects: list[str] = args.projects

    server_config_file_path = paths.configs_dir / "server.json"
    if not server_config_file_path.exists():
        logger.error(
            f"Configuration file '{server_config_file_path}' does not exist, is MCServer initialized yet?"
        )
        return 1

    server_config = config.read_config(
        "server", shared.default_configs["server"]["format_version"]
    )
    game_version: str = server_config["game_version"]
    loader_name: str = server_config["loader"]["name"]

    if not shared.support_mod(loader_name):
        logger.error(f"{loader_name.capitalize()} does not support mods")
        return 1

    project_label, project_directory = shared.get_loader_context(loader_name)
    if project_directory is None:
        logger.error("Wait 'project_directory' it can't be None! it just to satisfy pyright")
        return 1

    project_ids: list[str] = []
    project_versions: dict[str, ProjectVersion] = {}
    for project in projects:
        versions = modrinth_api.get_project_versions(
            project, loader_name, game_version, include_changelog=False
        )
        if len(versions) == 0:
            raise GetDependenciesError(
                f"Project has no version for '{loader_name.capitalize()}' '{game_version}'"
            )

        version = versions[0]
        project_id: str = version["project_id"]
        project_versions[project_id] = version
        project_ids.append(project_id)


    def get_version_dependencies(project_id: str) -> list[Dependency]:
        versions = modrinth_api.get_project_versions(
            project_id, loader_name, game_version, include_changelog=False
        )
        if len(versions) == 0:
            raise GetDependenciesError(
                f"Project has no version for '{loader_name.capitalize()}' '{game_version}'"
            )

        version = versions[0]
        project_versions[project_id] = version
        version_dependencies = version.get("dependencies")
        if version_dependencies is None:
            logger.debug(
                "Version for '{project_id}' did not have 'dependencies', returning an empty list"
            )
            version_dependencies = []

        return version_dependencies

    def get_dependencies(project_id: str) -> dict[str, int]:
        dependencies: list[Dependency] | None = None
        if project_id in project_versions:
            project_version = project_versions[project_id]
            if "dependencies" in project_version:
                dependencies = project_version["dependencies"]
        else:
            dependencies = get_version_dependencies(project_id)

        if dependencies is None:
            raise GetDependenciesError("No dependency provider available")

        return human_to_resolver(dependencies)

    resolved_dependencies = resolver.resolver_to_human(resolver.resolve_dependencies(
        project_ids, get_dependencies, resolver.required_only
    ))
    print(resolved_dependencies)

    required_dependencies: set[str] = set()
    incompatible_dependencies: set[str] = set()

    optional_projects: set[str] = set()
    required_projects: set[str] = set()
    incompatible_projects: set[str] = set()

    for project in resolved_dependencies:
        for dependencies in project["dependencies"]:
            match dependencies["dependency_type"]:
                case "required":
                    required_dependencies.add(dependencies["project_id"])
                case "incompatible":
                    incompatible_dependencies.add(dependencies["project_id"])

        project_id = project["project_id"]
        if project["is_manual"]:
            logger.debug(f"{project_id} is a manual mod, add it to the required bucket")
            required_projects.add(project_id)
            continue

        if "highest_type" not in project:
            logger.debug(f"{project_id} has no 'highest_type', this should be already handled by 'is_manual' but somehow it passed it")
            continue

        match project["highest_type"]:
            case "optional":
                optional_projects.add(project_id)
            case "required":
                required_projects.add(project_id)
            case "incompatible":
                incompatible_projects.add(project_id)

    print(f"""required_dependencies: {required_dependencies}
incompatible_dependencies: {incompatible_dependencies}

optional_projects: {optional_projects}
required_projects: {required_projects}
incompatible_projects: {incompatible_projects}""")

    conflicting_projects = required_dependencies & incompatible_dependencies
    if conflicting_projects:
        logger.error(f"Found conflicting dependencies: {', '.join(conflicting_projects)}")

    downloaded_projects: list[str] = list(required_projects)


    for project in downloaded_projects:
        project_version = project_versions[project]
        version_files = project_version["files"]

        primary_file = None
        for file in version_files:
            if file["is_primary"]:
                primary_file = file
                break
        
        if primary_file is None:
            primary_file = version_files[0]

        logger.info(f"Downloading {project_version['project_id']}?")
        project_directory.mkdir(exist_ok=True, parents=True)
        networking.download(primary_file['download_url'], project_directory / primary_file["file_name"])

    return 0


# import logging
# from argparse import Namespace

# from .. import config, paths, shared
# from ..modrinth import apis as modrinth_apis
# from ..modrinth import project_records
# from ..resolver import (
#     Dependency,
#     human_to_resolver,
#     required_only,
#     resolve_dependencies,
# )

# logger = logging.getLogger(__name__)


# def run(args: Namespace) -> int:
#     projects: list[str] = args.projects

#     if not (paths.configs_dir / "server.json").exists():
#         logger.error(
#             "Configuration file for server does not exist, is server initialized?"
#         )

#     server_config = config.read_config(
#         "server", shared.default_configs["server"]["format_version"]
#     )
#     game_version = server_config["game_version"]
#     loader_name = server_config["loader"]["name"]

#     if loader_name == "vanilla":
#         logger.error("Vanilla does not support mod or plugin.")
#         return 1

#     project_ids: list[str] = []
#     for project in projects:
#         modrinth_apis.get_project_versions(project, loader_name, game_version)

#     def get_dependencies(project_id: str) -> dict[str, int]:
#         dependencies: list[Dependency] = []
#         if project_records.record_exists(project_id):
#             project_record = project_records.read_record(project_id)
#             for dependency_id, dependency_type in project_record[
#                 "dependencies"
#             ].items():
#                 dependencies.append(
#                     {"project_id": dependency_id, "dependency_type": dependency_type}
#                 )

#         else:
#             project_version = modrinth_apis.get_project_versions(
#                 project_id, loader_name, game_version, include_changelog=False
#             )[0]

#             if "dependencies" in project_version:
#                 project_dependencies = project_version["dependencies"]
#                 for dependency in project_dependencies:
#                     if not "project_id" in dependency:
#                         continue

#                     if dependency["project_id"] is None:
#                         continue

#                     dependencies.append(
#                         {
#                             "project_id": dependency["project_id"],
#                             "dependency_type": dependency["dependency_type"],
#                         }
#                     )

#         return human_to_resolver(dependencies)

#     resolved_dependencies = resolve_dependencies(
#         projects, get_dependencies, required_only
#     )
#     print(resolved_dependencies)
#     return 0

#     # # from ..modrinth.apis import get_project_versions

#     # def get_project_versions(
#     #     project_id, loader_names, game_versions, featured=None, include_changelog=True
#     # ):
#     #     project_version = {
#     #         "embeddium": {
#     #             "dependencies": [
#     #                 {"project_id": "AANobbMI", "dependency_type": "incompatible"}
#     #             ],
#     #             "project_id": "sk9rgfiA",
#     #         },
#     #         "fabric-api": {"dependencies": [], "project_id": "P7dR8mSH"},
#     #         "jade": {
#     #             "dependencies": [
#     #                 {"project_id": "AANobbMI", "dependency_type": "required"},
#     #                 {"project_id": "u6dRKJwZ", "dependency_type": "optional"},
#     #             ],
#     #             "project_id": "nvQzSEkH",
#     #         },
#     #         "jei": {"dependencies": [], "project_id": "u6dRKJwZ"},
#     #         "just-enough-resources-jer": {
#     #             "dependencies": [
#     #                 {"project_id": "u6dRKJwZ", "dependency_type": "required"}
#     #             ],
#     #             "project_id": "uEfK2CXF",
#     #         },
#     #         "origins": {
#     #             "dependencies": [
#     #                 {"project_id": "P7dR8mSH", "dependency_type": "required"}
#     #             ],
#     #             "project_id": "3BeIrqZR",
#     #         },
#     #         "pehkui": {
#     #             "dependencies": [
#     #                 {"project_id": "P7dR8mSH", "dependency_type": "required"}
#     #             ],
#     #             "project_id": "t5W7Jfwy",
#     #         },
#     #         "podium": {
#     #             "dependencies": [
#     #                 {"project_id": "AANobbMI", "dependency_type": "required"}
#     #             ],
#     #             "project_id": "fW8woQj4",
#     #         },
#     #         "sodium": {"dependencies": [], "project_id": "AANobbMI"},
#     #         "thdilos-fox-origin-expanded": {
#     #             "dependencies": [
#     #                 {"project_id": "9qGn08Dr", "dependency_type": "required"},
#     #                 {"project_id": "3BeIrqZR", "dependency_type": "required"},
#     #                 {"project_id": "t5W7Jfwy", "dependency_type": "required"},
#     #             ],
#     #             "project_id": "CbsRGXBx",
#     #         },
#     #         "thdilos-fox-origin": {
#     #             "dependencies": [
#     #                 {"project_id": "3BeIrqZR", "dependency_type": "required"},
#     #                 {"project_id": "t5W7Jfwy", "dependency_type": "required"},
#     #             ],
#     #             "project_id": "9qGn08Dr",
#     #         },
#     #     }

#     #     id_slug = {
#     #         "3BeIrqZR": "origins",
#     #         "9qGn08Dr": "thdilos-fox-origin",
#     #         "AANobbMI": "sodium",
#     #         "CbsRGXBx": "thdilos-fox-origin-expanded",
#     #         "P7dR8mSH": "fabric-api",
#     #         "fW8woQj4": "podium",
#     #         "nvQzSEkH": "jade",
#     #         "sk9rgfiA": "embeddium",
#     #         "t5W7Jfwy": "pehkui",
#     #         "u6dRKJwZ": "jei",
#     #         "uEfK2CXF": "just-enough-resources-jer",
#     #     }

#     #     a = [
#     #         (
#     #             project_version[project_id]
#     #             if project_id in project_version
#     #             else project_version[id_slug[project_id]]
#     #         )
#     #     ]
#     #     return a

#     # server_config = config.read_config(
#     #     "server", shared.default_configs["server"]["format_version"]
#     # )
#     # loader_name = server_config["loader"]["name"]
#     # game_version = server_config["game_version"]

#     # cached_project_versions = {}
#     # project_ids = []

#     # for project in projects:
#     #     project_version = get_project_versions(
#     #         project, loader_name, game_version, include_changelog=False
#     #     )[0]

#     #     cached_project_versions[project_version["project_id"]] = project_version
#     #     project_ids.append(project_version["project_id"])

#     # id_to_slug: dict[str, str] = {}

#     # def get_dependencies(project_id: str) -> dict[str, int]:
#     #     dependencies: list[Dependency] = []

#     #     # Get the latest version
#     #     project_version = get_project_versions(
#     #         project_id, loader_name, game_version, include_changelog=False
#     #     )[0]
#     #     if "dependencies" in project_version:
#     #         project_dependencies = project_version["dependencies"]
#     #         for dependency in project_dependencies:
#     #             if not "project_id" in dependency:
#     #                 continue

#     #             if dependency["project_id"] is None:
#     #                 continue

#     #             dependencies.append(
#     #                 {
#     #                     "project_id": dependency["project_id"],
#     #                     "dependency_type": dependency["dependency_type"],
#     #                 }
#     #             )

#     #     return human_to_resolver(dependencies)

#     # def required_only(dependency_type: int) -> bool:
#     #     return dependency_type == 2

#     # resolved_projects = resolver_to_human(
#     #         resolve_dependencies(project_ids, get_dependencies, required_only)
#     #     )

#     # print(json.dumps(resolved_projects, indent=2))

#     # required_projects: set[str] = set()
#     # optional_projects: set[str] = set()
#     # incompatible_projects: set[str] = set()

#     # for project in resolved_projects:
#     #     for dependent in project["dependents"]:
#     #         match dependent["dependency_type"]:
#     #             case "required":
#     #                 required_projects.add(project["project_id"])
#     #             case "optional":
#     #                 optional_projects.add(project["project_id"])
#     #             case "incompatible":
#     #                 incompatible_projects.add(project["project_id"])

#     # conflicting_projects: set[str] = required_projects & incompatible_projects

#     # if conflicting_projects:
#     #     print(f"I think we have conflicting project -_-, like {conflicting_projects} are in required and incompatible")

#     # print(required_projects, optional_projects, incompatible_projects, conflicting_projects)

#     # return 0
