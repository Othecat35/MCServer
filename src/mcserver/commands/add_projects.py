import copy
import datetime
import json
import logging
from argparse import Namespace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TypedDict

from .. import config, networking, paths, resolver, shared
from ..modrinth import apis as modrinth_api
from ..modrinth import project_records, slug_index
from ..modrinth.project_records import ProjectRecordPayload
from ..modrinth.typings import (
    Dependency,
    DependencyType,
    ProjectInformation,
    ProjectVersion,
)
from ..resolver import Project

logger = logging.getLogger(__name__)


class GetDependenciesError(Exception):
    pass


class ResolverTranslationError(Exception):
    pass


class ProjectData(TypedDict):
    project_id: str
    is_manual: bool
    highest_type: DependencyType | None
    """Not present if the project is manual and has not dependents"""
    dependencies: list[Dependency]
    dependents: list[Dependency]


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


def resolver_to_human(dependency_graph: dict[str, Project]) -> list[ProjectData]:
    projects: list[ProjectData] = []
    for project_id, project in dependency_graph.items():
        dependencies: list[Dependency] = []
        for dependency_id, dependency_type in project["dependencies"].items():
            dependency: Dependency = {
                "project_id": dependency_id,
                "dependency_type": resolver.dependency_types2[dependency_type],
            }

            dependencies.append(dependency)

        dependents: list[Dependency] = []
        for dependency_id, dependency_type in project["dependents"].items():
            dependent: Dependency = {
                "project_id": dependency_id,
                "dependency_type": resolver.dependency_types2[dependency_type],
            }

            dependents.append(dependent)

        project_data: ProjectData = {
            "project_id": project_id,
            "is_manual": project["is_manual"],
            "highest_type": None,
            "dependencies": dependencies,
            "dependents": dependents,
        }

        if project["highest_type"] is not None:
            project_data["highest_type"] = resolver.dependency_types2[project["highest_type"]]

        projects.append(project_data)

    return projects


def run(args: Namespace) -> int:
    # argparse's args
    projects: list[str] = args.projects

    # server config
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

    # mod compatibility test
    if not shared.support_mod(loader_name):
        logger.error(f"{loader_name.capitalize()} does not support mods")
        return 1

    # mod vs project labeling
    project_label, project_directory = shared.get_loader_context(loader_name)
    if project_directory is None:
        logger.error("Wait 'project_directory' it can't be None! it just to satisfy pyright")
        return 1

    # initial project normalizer (slug -> id) + cache
    project_ids: list[str] = []
    project_versions: dict[str, ProjectVersion] = {}
    for project in projects:
        project_id = slug_index.slug_to_id(project)
        if project_records.record_exists(project_id):
            project_ids.append(project_id)
            logger.debug(f"Skipping fecthing for {project_id}, record already exist")
            continue

        versions = modrinth_api.get_project_versions(
            project, loader_name, game_version, include_changelog=False
        )

        if len(versions) == 0:
            raise GetDependenciesError(
                f"Project has no version for '{loader_name.capitalize()}' '{game_version}'"
            )

        version = versions[0]
        project_id = version["project_id"]
        if project != project_id:
            logger.debug("project and project_id is diffrent, adding it to the slug index")
            slug_index.update_slug_index(project, project_id)

        project_id: str = version["project_id"]
        project_versions[project_id] = version
        project_ids.append(project_id)

    # save the slug index
    slug_index.save_slug_index()

    # get dependencies from Modrinth version
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

    # Dependency provider
    loaded_project_records: dict[str, ProjectRecordPayload] = {}
    def get_dependencies(project_id: str) -> dict[str, int]:
        dependencies: list[Dependency] | None = None
        if project_records.record_exists(project_id):
            project_record = project_records.read_record(project_id)
            loaded_project_records[project_id] = project_record
            return project_record["dependencies"]

        if project_id in project_versions:
            project_version = project_versions[project_id]
            if "dependencies" in project_version:
                dependencies = project_version["dependencies"]
        else:
            dependencies = get_version_dependencies(project_id)

        if dependencies is None:
            raise GetDependenciesError(f"No dependency provider available for {project_id}")

        return human_to_resolver(dependencies)

    # resolve dependencies
    resolved_projects = resolver_to_human(resolver.resolve_dependencies(project_ids, get_dependencies, resolver.required_only))
    resolved_data: dict = {}
    for project in resolved_projects:
        project = copy.deepcopy(project)
        project_id = str(project.pop("project_id"))
        resolved_data[project_id] = project

    # project buckets
    all_project_ids: set[str] = set()
    required_dependencies: set[str] = set()
    incompatible_dependencies: set[str] = set()

    optional_projects: set[str] = set()
    required_projects: set[str] = set()
    incompatible_projects: set[str] = set()

    for project in resolved_projects:
        project_id = project["project_id"]
        all_project_ids.add(project_id)
        for dependency in project["dependencies"]:
            if "project_id" not in dependency or dependency["project_id"] is None:
                logger.debug("A dependency lacks project ID or it is None")
                continue

            match dependency["dependency_type"]:
                case "required":
                    required_dependencies.add(dependency["project_id"])
                case "incompatible":
                    incompatible_dependencies.add(dependency["project_id"])

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

    # debugging
    print(f"""all_project_ids: {all_project_ids}
required_dependencies: {required_dependencies}
incompatible_dependencies: {incompatible_dependencies}

optional_projects: {optional_projects}
required_projects: {required_projects}
incompatible_projects: {incompatible_projects}""")

    # conflict detection
    conflicting_projects = required_dependencies & incompatible_dependencies
    if conflicting_projects:
        logger.error(f"Found conflicting dependencies: {', '.join(conflicting_projects)}")

    # fetch additional info
    project_informations: dict[str, ProjectInformation] = {}
    #for project in json.loads(Path("a.json").read_text()): 
    for project in modrinth_api.get_project_informations(list(all_project_ids)):
        project_id = project["project_id"]
        project_informations[project_id] = project

    for project_information in project_informations.values():
        project_slug = project_information.get("project_slug")
        if project_slug is None:
            continue

        slug_index.update_slug_index(project_slug, project_information["project_id"])

    slug_index.save_slug_index()

    #info display
    required_projects_count = len(required_projects)
    logger.info(f"{shared.pluralize(project_label, required_projects_count).capitalize()} that {shared.pluralize('is', required_projects_count)} going to be downloaded:")
    required_project_display: list[str] = []
    for project_id in list(required_projects):
        required_project_display.append(f"{project_informations[project_id]['project_name']} ({project_id})")

    required_project_display.sort()
    print(", ".join(required_project_display))

    optional_projects_count = len(optional_projects)
    if optional_projects:
        logger.info(f"{shared.pluralize(project_label, optional_projects_count).capitalize()} that {shared.pluralize('is', optional_projects_count)} optional:")
        optional_project_display: list[str] = []
        for project_id in list(optional_projects):
            optional_project_display.append(f"{project_informations[project_id]['project_name']} ({project_id})")

        optional_project_display.sort()
        print(", ".join(optional_project_display))

    incompatible_projects_count = len(optional_projects)
    if incompatible_projects:
        logger.info(f"{shared.pluralize(project_label, incompatible_projects_count).capitalize()} that {shared.pluralize('is', incompatible_projects_count)} incompatible:")
        incompatible_project_display: list[str] = []
        for project_id in list(incompatible_projects):
            incompatible_project_display.append(f"{project_informations[project_id]['project_name']} ({project_id})")

        incompatible_project_display.sort()
        print(", ".join(incompatible_project_display))

    # confirmation prompt
    confirmation_answer = shared.confirmation_prompt("Do you want to continue?", default_option=True)

    if not confirmation_answer:
        print("Cancelled")
        return 1



    for project_id in required_projects:
        project_data = resolved_data[project_id]
        project_information = project_informations[project_id]
        project_version = project_versions.get(project_id)
        project_record = loaded_project_records.get(project_id)

        if project_version is not None:
            version_files = project_version["files"]

            primary_file = None
            for file in version_files:
                if file["is_primary"]:
                    primary_file = file
                    break

            if primary_file is None:
                primary_file = version_files[0]


            record_payload: ProjectRecordPayload = {
                "project_name": project_information["project_name"],
                "project_slug": project_information.get("project_slug"),
                "version_id": project_version["version_id"],
                "version_environment": project_version["environment"],
                "file": primary_file,
                "added_time": datetime.now(tz=UTC).isoformat(),
                "discovered_time": datetime.now(tz=UTC).isoformat(),
                "updated_time": None,
                "is_manual": project_data["is_manual"],
                "highest_type": project_data["highest_type"],
                "dependencies": human_to_resolver(project_data["dependencies"]),
                "dependents": human_to_resolver(project_data["dependents"])
            }

            # logger.info(f"Downloading {project_information['project_name']}...")
            # project_directory.mkdir(exist_ok=True, parents=True)
            # networking.download(primary_file['download_url'], project_directory / primary_file["file_name"])
            # project_records.write_record(project_id, record_payload)
        elif project_record is not None:
            record_payload = copy.deepcopy(project_record)
            record_payload["dependencies"].update(project_data["dependencies"])
            record_payload["dependents"].update(project_data["dependents"])
            record_payload.update({
                "updated_time": datetime.now(tz=UTC).isoformat(),
                "is_manual": project_record["is_manual"] or project_data["is_manual"],
            })

            primary_file = record_payload["file"]

            logger.info(f"Downloading {project_information['project_name']}...")
            if primary_file is None:
                logger.error("Screw you")
                continue

            # networking.download(primary_file["download_url"], project_directory / primary_file["file_name"])
            project_records.write_record(project_id, record_payload)










    # # download required mods
    # for project_id in required_projects:
    #     project_version = project_versions.get(project_id)
    #     project_information = project_informations[project_id]
    #     project_data = resolved_data[project_id]
    #     project_record = loaded_project_records.get(project_id)

    #     if project_record is not None:
    #         record_payload = copy.deepcopy(project_record)
    #         record_payload["dependencies"].update(project_data["dependencies"])
    #         record_payload["dependents"].update(project_data["dependents"])
    #         record_payload.update({
    #             "updated_time": datetime.now(tz=UTC).isoformat(),
    #             "is_manual": project_record["is_manual"] or project_data["is_manual"],
    #         })
    #     elif project_version:
    #     project_records.write_record(project_id, record_payload)

    # for project_id in all_project_ids:
    #     if 
    #     project_records.write_record(project_id, record_payload)

    #     project_data = resolved_data[project_id]
    #     project_information = project_informations[project_id]
    #     project_record = loaded_project_records.get(project_id)
    #     project_version = project_versions.get(project_id)

    #     record_payload: ProjectRecordPayload = {
    #         "project_name": project_information["project_name"],
    #         "project_slug": project_information.get("project_slug"),
    #         "version_id": None,
    #         "version_environment": None,
    #         "file": None,
    #         "added_time": None,
    #         "discovered_time": datetime.now(tz=UTC).isoformat(),
    #         "updated_time": None,
    #         "is_manual": project_data["is_manual"],
    #         "highest_type": project_data["highest_type"],
    #         "dependencies": human_to_resolver(project_data["dependencies"]),
    #         "dependents": human_to_resolver(project_data["dependents"]),
    #     }

    #     if project_id in required_projects:
    #         record_payload["added_time"] = datetime.now(tz=UTC).isoformat()

    #     if project_version is not None:
    #         version_files = project_version["files"]

    #         primary_file = None
    #         for file in version_files:
    #             if file["is_primary"]:
    #                 primary_file = file
    #                 break
            
    #         if primary_file is None:
    #             primary_file = version_files[0]

    #         record_payload.update({
    #             "version_id": project_version["version_id"],
    #             "version_environment": project_version["environment"],
    #             "file": primary_file
    #         })

    #     if project_record is not None:
    #         record_payload["dependencies"].update(project_record["dependencies"])
    #         record_payload["dependents"].update(project_record["dependents"])
    #         record_payload.update({
    #             "added_time": project_record["added_time"],
    #             "updated_time": datetime.now(tz=UTC).isoformat()
    #         })

    #     project_records.write_record(project_id, record_payload)

    #     record_payload: ProjectRecordPayload = {
    #         "project_name": project_info["project_name"],
    #         "project_slug": project_info["project_slug"],
    #         "version_id": project_version["version_id"],
    #         "version_environment": project_version["environment"],
    #         "added_time": datetime.now(tz=UTC).isoformat(),
    #         "updated_time": None,
    #         "file": primary_file,
    #         "is_manual": project_data["is_manual"],
    #         "highest_type": project_data["highest_type"],
    #         "dependencies": project_data["dependencies"],
    #         "dependents": project_data["dependents"]
    #     }

    #     loaded_project_record = loaded_project_records.get(project_id, {})
    #     project_records.write_record(project_id, record_payload)

    # for project_id in optional_projects:
    #     project_data = resolved_data[project_id]
    #     project_info = project_information[project_id]
    #     loaded_project_record = loaded_project_records.get(project_id)
    #     record_payload: ProjectRecordPayload = {
    #         "project_name": project_info["project_name"],
    #         "project_slug": project_info["project_slug"],
    #         "added_time": None,
    #         "updated_time": None,
    #         "is_manual": project_data["is_manual"],
    #         "highest_type": project_data["highest_type"],
    #         "dependencies": project_data["dependencies"],
    #         "dependents": project_data["dependents"]
    #     }

    #     if loaded_project_record is not None:
    #         if updated_time

    #     project_records.write_record(project_id, record_payload)


    # for project in resolved_projects:
    #     project_id = project["project_id"]
    #     project_information = project_info[project_id]
    #     project_version = project_versions[project_id]

    #     record_payload: ProjectRecordPayload = {
    #         "project_name": project_information["project_name"],
    #         "project_slug": project_information["project_slug"],
    #         "version_id": project_version["version_id"],
    #         "version_environment": project_version["environment"],
    #         "added_time": datetime.now(tz=UTC).isoformat(),
    #         "file": primary_file,
    #         "is_manual": project["is_manual"],
    #         "highest_type": project["highest_type"],
    #         "dependencies": project["dependencies"],
    #         "dependents": project["dependents"],
    #     }

    #     project_records.write_record(project["project_id"], record_payload)

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

#     resolved_projects = resolve_dependencies(
#         projects, get_dependencies, required_only
#     )
#     print(resolved_projects)
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
