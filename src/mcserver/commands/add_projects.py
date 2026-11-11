import json
import logging
from argparse import Namespace

from .. import config, paths, resolver, shared
from ..modrinth import apis as modrinth_api
from ..modrinth.typings import (
    Dependency,
    DependencyType,
    ProjectInformation,
    ProjectVersion,
)
from ..resolver import ProjectData

logger = logging.getLogger(__name__)

dependency_types: dict[DependencyType, int] = {
    "embedded": 0,
    "optional": 1,
    "required": 2,
    "incompatible": 3,
}

class GetVersionError(Exception): pass
class GetDependenciesError(Exception): pass
class ResolverTranslationError(Exception):
    pass

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

    if not (paths.configs_dir / "server.json").exists():
        logger.error("Configuration file for server does not exist, is server initialized?")
        return 1

    server_config = config.read_config("server", shared.default_configs["server"]["format_version"])
    game_version: str = server_config["game_version"]
    loader_name: str = server_config["loader"]["name"]

    project_label, project_directory = shared.get_loader_context(loader_name)

    project_ids: list[str] = []
    project_versions: dict[str, ProjectVersion] = {}
    for project in projects:
        versions = modrinth_api.get_project_versions(project, loader_name, game_version, include_changelog=True)
        if len(versions) == 0:
            raise GetVersionError(f"{project} has no version for {loader_name.capitalize()} {game_version}")

        project_version = versions[0]
        project_id = project_version["project_id"]
        project_versions[project_id] = project_version
        project_ids.append(project_id)

    def get_project_dependencies(project_id: str) -> list[Dependency]:
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

    def get_dependencies(project_id) -> dict[str, int]:
        dependencies: list[Dependency] | None = None
        if project_id in project_versions:
            project_version = project_versions[project_id]
            if "dependencies" in project_version:
                dependencies = project_version["dependencies"]
        else:
            dependencies = get_project_dependencies(project_id)

        if dependencies is None:
            raise GetDependenciesError(f"No dependency provider available for {project_id}")

        return human_to_resolver(dependencies)


    resolved_projects: list[ProjectData] = resolver.resolver_to_human(resolver.resolve_dependencies(project_ids, get_dependencies, resolver.required_only))

    print(json.dumps(resolved_projects, indent=2))

    all_project_ids: set[str] = set()
    incompatible_dependencies: set[str] = set()
    required_dependencies: set[str] = set()

    optional_projects: set[str] = set()
    required_projects: set[str] = set()
    incompatible_projects: set[str] = set()

    # Putting projects and dependencies into its bucket
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

    # Conflict detection
    conflicting_projects = required_dependencies & incompatible_dependencies
    if conflicting_projects:
        logger.error(f"Found conflicting dependencies: {', '.join(conflicting_projects)}")

    # fetch additional info
    project_informations: dict[str, ProjectInformation] = {}
    for project in modrinth_api.get_project_informations(list(all_project_ids)):
        project_informations[project["project_id"]] = project

    # Display information
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

    incompatible_projects_count = len(incompatible_projects)
    if incompatible_projects:
        logger.info(f"{shared.pluralize(project_label, incompatible_projects_count).capitalize()} that {shared.pluralize('is', incompatible_projects_count)} incompatible:")
        incompatible_project_display: list[str] = []
        for project_id in list(incompatible_projects):
            incompatible_project_display.append(f"{project_informations[project_id]['project_name']} ({project_id})")

        incompatible_project_display.sort()
        print(", ".join(incompatible_project_display))

    # Confirmation prompt
    confirmation_answer = shared.confirmation_prompt("Do you want to continue?", default_option=True)

    if not confirmation_answer:
        print("Cancelled")
        return 1

    for project_id in required_projects:
        pass

    return 0