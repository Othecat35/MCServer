import logging
from argparse import Namespace
from datetime import UTC, datetime
from pathlib import Path

from .. import config, modrinth, networking, paths, resolver, shared
from ..modrinth import project_records, slug_index
from ..modrinth.project_records import ProjectRecordData, ProjectRecordPayload
from ..modrinth.typings import (
    Dependency,
    DependencyType,
    ProjectInformation,
    ProjectVersion,
    VersionDependency,
)
from ..resolver import ProjectData

logger: logging.Logger = logging.getLogger(__name__)

dependency_types: dict[DependencyType, int] = {
    "embedded": 0,
    "optional": 1,
    "required": 2,
    "incompatible": 3,
}


class GetVersionError(Exception):
    pass


class GetDependenciesError(Exception):
    pass


class ResolverTranslationError(Exception):
    pass


def version_dependencies_to_dependencies(
    version_dependencies: list[VersionDependency],
) -> list[Dependency]:
    dependencies: list[Dependency] = []
    for version_dependency in version_dependencies:
        dependency: Dependency = {
            "dependency_type": version_dependency["dependency_type"]
        }

        if "project_id" in version_dependency:
            dependency["project_id"] = version_dependency["project_id"]

        dependencies.append(dependency)

    return dependencies


def human_to_resolver(dependencies: list[Dependency]) -> dict[str, int]:
    resolver_dependencies: dict[str, int] = {}
    for dependency in dependencies:
        if "project_id" not in dependency:
            raise ResolverTranslationError("'project_id' does not exist in dependency")

        dependency_id: str | None = dependency["project_id"]
        if dependency_id is None:
            raise ResolverTranslationError("'project_id' is None")

        if dependency["dependency_type"] == "embedded":
            logger.debug("Skipping 'embedded' dependency")
            continue

        resolver_dependencies[dependency_id] = dependency_types[
            dependency["dependency_type"]
        ]

    return resolver_dependencies


def add_projects(args: Namespace) -> int:
    paths.update_working_dir(args.directory)
    projects: list[str] = args.projects

    if not config.config_exists("server"):
        logger.error(
            "Configuration file for 'server' does not exist, is server initialized?"
        )
        return 1

    server_config: dict = config.read_config(
        "server", shared.default_configs["server"]["format_version"]
    )
    game_version: str = server_config["game_version"]
    loader_name: str = server_config["loader"]["name"]

    # mod/plugin compatibility check
    if not shared.supports_mod(loader_name):
        logger.error(f"{loader_name.capitalize()} does not support mods")
        return 1

    # mod vs project labeling
    project_label, project_directory = shared.get_loader_context(loader_name)
    if project_directory is None:
        logger.error(
            "Wait 'project_directory' it can't be None! it just to satisfy pyright"
        )
        return 1

    project_ids: list[str] = []
    version_cache: dict[str, ProjectVersion] = {}
    for project in projects:
        if slug_index.is_slug_indexed(project):
            project_id: str = slug_index.slug_to_id(project)
            project_ids.append(project_id)
            continue

        try:
            versions: list[modrinth.ProjectVersion] = modrinth.get_project_versions(
                project, loader_name, game_version, include_changelog=False
            )
        except modrinth.GetProjectVersionsError:
            logger.error("Failed to get project versions!")
            return 1

        if len(versions) == 0:
            logger.error(
                f"{project} has no version for {loader_name.capitalize()} {game_version}"
            )

        project_version = versions[0]
        project_id: str = project_version["project_id"]
        version_cache[project_id] = project_version
        project_ids.append(project_id)

    record_cache: dict[str, ProjectRecordData] = {}

    def get_project_dependencies(project_id: str) -> list[Dependency]:
        if project_records.record_exists(project_id):
            project_record: ProjectRecordData = project_records.read_record(project_id)
            record_cache[project_id] = project_record

            project_dependencies: list[modrinth.Dependency] = project_record["dependencies"]
            return project_dependencies

        versions: list[modrinth.ProjectVersion] = modrinth.get_project_versions(
            project_id, loader_name, game_version, include_changelog=False
        )
        if len(versions) == 0:
            raise GetDependenciesError(
                f"Project has no version for '{loader_name.capitalize()}' '{game_version}'"
            )

        version: modrinth.ProjectVersion = versions[0]
        version_cache[project_id] = version
        version_dependencies: list[VersionDependency] | None = version.get(
            "dependencies"
        )
        if version_dependencies is None:
            logger.debug(
                "Version for '{project_id}' did not have 'dependencies', returning an empty list"
            )
            version_dependencies = []

        return version_dependencies_to_dependencies(version_dependencies)

    def get_dependencies(project_id) -> dict[str, int]:
        dependencies: list[Dependency] | None = None
        if project_id in version_cache:
            project_version: ProjectVersion = version_cache[project_id]
            if "dependencies" in project_version:
                dependencies: list[Dependency] | None = version_dependencies_to_dependencies(
                    project_version["dependencies"]
                )
        else:
            dependencies: list[Dependency] | None = get_project_dependencies(project_id)

        if dependencies is None:
            raise GetDependenciesError(
                f"No dependency provider available for {project_id}"
            )

        return human_to_resolver(dependencies)

    try:
        resolved_projects: list[ProjectData] = resolver.resolver_to_human(
            resolver.resolve_dependencies(
                project_ids, get_dependencies, resolver.required_only
            )
        )
    except modrinth.GetProjectVersionsError:
        logger.error("Failed to get project versions!")
        return 1

    resolved_project_data: dict[str, ProjectData] = {}
    for project in resolved_projects:
        resolved_project_data[project["project_id"]] = project

    all_project_ids: set[str] = set()
    incompatible_dependencies: set[str] = set()
    required_dependencies: set[str] = set()

    optional_projects: set[str] = set()
    required_projects: set[str] = set()
    incompatible_projects: set[str] = set()

    # Putting projects and dependencies into its bucket
    for project in resolved_projects:
        project_id: str = project["project_id"]
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
            logger.debug(
                f"{project_id} has no 'highest_type', this should be already handled by 'is_manual' but somehow it passed it"
            )
            continue

        match project["highest_type"]:
            case "optional":
                optional_projects.add(project_id)
            case "required":
                required_projects.add(project_id)
            case "incompatible":
                incompatible_projects.add(project_id)

    # Conflict detection
    conflicting_projects: set[str] = required_dependencies & incompatible_dependencies
    if conflicting_projects:
        logger.error(
            f"Found conflicting dependencies: {', '.join(conflicting_projects)}"
        )
        logger.error("Cannot continue.")
        return 1

    # fetch additional info
    project_informations: dict[str, ProjectInformation] = {}
    for project in modrinth.get_project_informations(list(all_project_ids)):
        project_informations[project["project_id"]] = project

    # Display information
    required_projects_count: int = len(required_projects)
    logger.info(
        f"{shared.pluralize(project_label, required_projects_count).capitalize()} that {shared.pluralize('is', required_projects_count)} going to be downloaded:"
    )
    required_project_display: list[str] = []
    for project_id in list(required_projects):
        required_project_display.append(
            f"{project_informations[project_id]['project_name']} ({project_id})"
        )

    required_project_display.sort()
    print(f"  {', '.join(required_project_display)}\n")

    optional_projects_count: int = len(optional_projects)
    if optional_projects:
        logger.info(
            f"{shared.pluralize(project_label, optional_projects_count).capitalize()} that {shared.pluralize('is', optional_projects_count)} optional:"
        )
        optional_project_display: list[str] = []
        for project_id in list(optional_projects):
            optional_project_display.append(
                f"{project_informations[project_id]['project_name']} ({project_id})"
            )

        optional_project_display.sort()
        print(f"  {', '.join(optional_project_display)}\n")

    incompatible_projects_count: int = len(incompatible_projects)
    if incompatible_projects:
        logger.info(
            f"{shared.pluralize(project_label, incompatible_projects_count).capitalize()} that {shared.pluralize('is', incompatible_projects_count)} incompatible:"
        )
        incompatible_project_display: list[str] = []
        for project_id in list(incompatible_projects):
            incompatible_project_display.append(
                f"{project_informations[project_id]['project_name']} ({project_id})"
            )

        incompatible_project_display.sort()
        print(f"  {', '.join(incompatible_project_display)}\n")

    # Confirmation prompt
    confirmation_answer: bool = shared.confirmation_prompt(
        "Do you want to continue?", default_option=True
    )

    if not confirmation_answer:
        print("Cancelled.")
        return 1

    for project_id in required_projects:
        project_data: ProjectData = resolved_project_data[project_id]
        project_information: ProjectInformation = project_informations[project_id]
        if project_id not in version_cache:
            project_record = record_cache[project_id]
            primary_file: modrinth.File | None = project_record["file"]

            if primary_file is None:
                logger.error(f"Project record of {project_id} has no version file")
                return 1

            file_path: Path = project_directory / primary_file["file_name"]
            if file_path.exists():
                logger.info(f"File '{file_path}' already exist, skipping download")
                continue

            logger.info(f"Downloading {project_information['project_name']}...")
            project_directory.mkdir(exist_ok=True, parents=True)

            sha512_hash: str | None = primary_file["file_hashes"].get("sha512")
            if sha512_hash is not None:
                networking.download(
                    primary_file["download_url"], file_path, hashes={"sha512": sha512_hash}
                )
            else:
                networking.download(primary_file["download_url"], file_path)
        else:
            project_version = version_cache[project_id]
            version_files: list[modrinth.File] = project_version["files"]

            primary_file: modrinth.File | None = None
            for file in version_files:
                if file["is_primary"]:
                    primary_file: modrinth.File | None = file
                    break

            if primary_file is None:
                primary_file: modrinth.File | None = version_files[0]

            file_path: Path = project_directory / primary_file["file_name"]
            if file_path.exists():
                logger.info(f"File '{file_path}' already exist, skipping download")
                continue

            logger.info(f"Downloading {project_information['project_name']}...")
            project_directory.mkdir(exist_ok=True, parents=True)

            sha512_hash: str | None = primary_file["file_hashes"].get("sha512")
            if sha512_hash is not None:
                networking.download(
                    primary_file["download_url"], file_path, hashes={"sha512": sha512_hash}
                )
            else:
                networking.download(primary_file["download_url"], file_path)

    for project_data in resolved_projects:
        project_id: str = project_data["project_id"]

        project_information = project_informations[project_id]
        project_version = version_cache.get(project_id)

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
                "project_name": project_information.get("project_name"),
                "project_slug": project_information.get("project_slug"),
                "version_id": project_version["version_id"],
                "version_environment": project_version["environment"],
                "file": primary_file,
                "added_time": datetime.now(tz=UTC).isoformat(),
                "discovered_time": datetime.now(tz=UTC).isoformat(),
                "updated_time": None,
                "is_manual": project_data["is_manual"],
                "highest_type": project_data["highest_type"],
                "dependencies": project_data["dependencies"],
                "dependents": project_data["dependents"],
            }
        else:
            record_payload: ProjectRecordPayload = {
                "project_name": project_information.get("project_name"),
                "project_slug": project_information.get("project_slug"),
                "version_id": None,
                "version_environment": None,
                "file": None,
                "added_time": None,
                "discovered_time": datetime.now(tz=UTC).isoformat(),
                "updated_time": None,
                "is_manual": project_data["is_manual"],
                "highest_type": project_data["highest_type"],
                "dependencies": project_data["dependencies"],
                "dependents": project_data["dependents"],
            }

        project_records.write_record(project_id, record_payload)

    for project_information in project_informations.values():
        project_slug = project_information.get("project_slug")
        if project_slug is None:
            continue

        slug_index.update_slug_index(project_slug, project_information["project_id"])

    slug_index.save_slug_index()

    logger.info("Complete!")
    return 0
