#Modules
# Standard
import argparse, json, math, os, shutil, sys, textwrap
import logging as log

from pathlib import Path
from collections import deque

# MCServer
from config import default_configs, generate_config, load_config
from constants import __version__
from indexing import project_index_exists, create_project_index, read_project_index, slug_to_id, slug_id_file, slug_id, indexes_dir, update_project_index
from metadata import metadata_file
from modrinth.api import get_project_versions, VersionDependency, modrinth_base_api
from networking import download, request
from shared import ansi, mcserver_dir, mod_environment_color, pluralize, format_number, wrap_ansi, confirmation_prompt
from state import get_state, set_state, is_active

import config
import state
import fabricmc.meta
import mojang.eula, mojang.manifest
import modrinth.modpack
import networking
import papermc.api
import purpurmc.api

#Variables
debug_mode = os.getenv("MCSERVER_DEBUG") == "1"
log_level = log.DEBUG if debug_mode else log.INFO

mods_loader = ["fabric"]
plugins_loader = ["paper", "purpur"]
loaders_list = ["vanilla"] + mods_loader + plugins_loader

eula_agree_sentence = "Yes, I agree."

# Severity levels
version_dependency_types = {
    "embedded": 0,
    "optional": 1,
    "required": 2,
    "incompatible": 3
}

#Paths
mods_dir = Path("mods")
plugins_dir = Path("plugins")

configs_dir = mcserver_dir / "configs"
tempfiles_dir = mcserver_dir / "tempfiles"

#Error Classes
class AddProjectsError(Exception): pass
class InitializeServerError(Exception): pass
class InstallServerError(Exception): pass
class SearchProjectsError(Exception): pass
class ShowProjectsError(Exception): pass

class EULAAgreementError(Exception): pass
class FetchProjectVersionError(Exception): pass
class DownloadURLError(Exception): pass

class ResolveProjectsConflictsError(Exception):
    def __init__(self, project_id: str, incompatible_dependants: list | str, required_dependants: list | str | None = None):
        if required_dependants is None: required_dependants = []
        if isinstance(required_dependants, str): required_dependants = [required_dependants]
        if isinstance(incompatible_dependants, str): incompatible_dependants = [incompatible_dependants]

        required_join = "', '".join(required_dependants)
        required_message = f" but required by '{required_join}'" if required_dependants else " but it is requested"

        incompatible_join = "', '".join(incompatible_dependants)
        super().__init__(f"Project '{project_id}' is incompatible with '{incompatible_join}'{required_message}")

        self.project_id = project_id

        self.incompatible_dependants = incompatible_dependants
        self.required_dependants = required_dependants

#Functions
def print_help(args):
    args.parser.print_help()
    sys.exit(0)

def hahaha_yes():
    print("The cake is a lie.")
    sys.exit(0)

def wrap_string(string: str, initial_indent: str | int = "", subsequent_indent: str | int = "", width: int | None = None):
    if isinstance(initial_indent, int):
        initial_indent = " " * initial_indent

    if isinstance(subsequent_indent, int):
        subsequent_indent = " " * subsequent_indent

    terminal_width = width or shutil.get_terminal_size().columns
    return "\n".join(textwrap.wrap(string, width=terminal_width, initial_indent=initial_indent, subsequent_indent=subsequent_indent))

project_label = "project"
loader_dir = None

def set_loader_context(loader_name: str):
    global project_label
    global loader_dir

    if loader_name in mods_loader:
        project_label = "mod"
        loader_dir = mods_dir
    elif loader_name in plugins_loader:
        project_label = "plugin"
        loader_dir = plugins_dir

# Resolve prejects dependencies
def adapt_dependencies_data(dependencies: list[VersionDependency]) -> dict:
    dependencies_data = {}
    for dependency in dependencies:
        if "project_id" in dependency:
            if dependency["project_id"] is not None and dependency["dependency_type"] != version_dependency_types["embedded"]:
                dependencies_data[dependency["project_id"]] = version_dependency_types[dependency["dependency_type"]]

    return dependencies_data

def filter_dependencies_type(dependencies: dict, filter_type: str):
    dependencies_list = []
    for dependency_id, dependency_type in dependencies.items():
        if dependency_type == version_dependency_types[filter_type]:
            dependencies_list.append(dependency_id)

    return dependencies_list

def resolve_projects(projects_id: list | str, game_version: str, loader_name: str) -> dict:
    projects_id = list(projects_id)
    unresolved_ids = deque()
    resolved_data = {}

    # Initial seeding
    for project_id in projects_id:
        project_id = slug_to_id(project_id)

        log.debug(f"Adding project '{project_id}' as unresolved")
        unresolved_ids.append(project_id)
        resolved_data[project_id] = {
            "metadata": {},
            "relationship": {
                "manual": True,
                "type": version_dependency_types["required"],
                "dependencies": {},
                "dependants": {}
            }
        }

    # Main code
    while unresolved_ids:
        project_id = unresolved_ids.popleft()

        project_data = resolved_data.pop(project_id)
        project_metadata = project_data["metadata"]
        project_relationship = project_data["relationship"]

        log.debug(f"Processing project '{project_id}'")

        skip_fetch_version = False

        if project_index_exists(project_id):
            project_index_data = read_project_index(project_id)

            project_index_relationship = project_index_data["relationship"]
            project_dependency_type = project_index_relationship["type"]

            if project_dependency_type == version_dependency_types["incompatible"]:
                project_dependants = project_index_relationship["dependants"]

                incompatible_dependants = filter_dependencies_type(project_dependants, "incompatible")
                required_dependants = filter_dependencies_type(project_dependants, "required")
                raise ResolveProjectsConflictsError(project_id, incompatible_dependants, required_dependants)

            log.debug("Project index exists, using it as cache")
            project_index_relationship["dependants"].update(project_relationship["dependants"])
            if project_relationship["manual"]:
                project_index_relationship["manual"] = True

            project_data = project_index_data
            skip_fetch_version = True

        if not skip_fetch_version:
            log.debug("Fetching project version")
            version = get_project_versions(project_id, game_version, loader_name)[0]
            project_id = version["project_id"]

            # Check if entry with project ID still exists (meaning we're still using slug)
            if project_id in resolved_data:
                log.debug(f"Found existing data with ID {project_id}")
                existing_entry = resolved_data.pop(project_id)
                existing_entry_relationship = existing_entry["relationship"]

                # Check if existing entry is marked as incompatible
                if existing_entry_relationship["type"] == version_dependency_types["incompatible"]:
                    incompatible_dependants = filter_dependencies_type(existing_entry_relationship["dependants"], "incompatible")
                    raise ResolveProjectsConflictsError(project_id, incompatible_dependants)

                log.debug(f"Keeping existing data")
                project_relationship["dependants"].update(existing_entry_relationship["dependants"])

            if "version_id" in version:
                project_metadata["version_id"] = version["version_id"]

            if "version_name" in version:
                project_metadata["version_name"] = version["version_name"]
            
            if "version_number" in version:
                project_metadata["version_number"] = version["version_number"]

            if "dependencies" in version:
                project_relationship["dependencies"] = adapt_dependencies_data(version["dependencies"])

        for dependency_id, dependency_type in project_relationship["dependencies"].items():
            if dependency_id in resolved_data:
                dependency_data = resolved_data[dependency_id]
                dependency_data_relationship = dependency_data["relationship"]

                dependency_data_type = dependency_data_relationship["type"]
                dependency_data_dependants = dependency_data_relationship["dependants"]

                if dependency_type == version_dependency_types["required"]:
                    if dependency_data_type == version_dependency_types["incompatible"]:
                        incompatible_dependants = filter_dependencies_type(dependency_data_dependants, "incompatible")
                        raise ResolveProjectsConflictsError(dependency_id, incompatible_dependants, project_id)
                    elif dependency_data_type == version_dependency_types["optional"]:
                        log.debug(f"Adding initially optional dependency '{project_id}' to unresolved")
                        unresolved_ids.append(dependency_id)
                elif dependency_type == version_dependency_types["incompatible"] and dependency_data_type == version_dependency_types["required"]:
                    required_dependants = filter_dependencies_type(dependency_data_dependants, "required")
                    raise ResolveProjectsConflictsError(dependency_id, project_id, required_dependants)

                log.debug(f"Updating project data '{dependency_id}' with new '{dependency_type}' type dependant")
                dependency_data_dependants[project_id] = dependency_type
                dependency_data_relationship["type"] = max(dependency_data_relationship["type"], dependency_type)
            else:
                log.debug(f"Adding new project entry for dependency: {dependency_id}")
                resolved_data[dependency_id] = {
                    "metadata": {},
                    "relationship": {
                        "manual": False,
                        "type": dependency_type,
                        "dependencies": {},
                        "dependants": {
                            project_id: dependency_type
                        }
                    }
                }

                # Only process required mods
                if dependency_type == version_dependency_types["required"]:
                    unresolved_ids.append(dependency_id)

        resolved_data[project_id] = project_data

    # Populate resolved_data with even more data
    fetch_ids = []
    for project_id, project_data in resolved_data.items():
        #If project data doesn't have slug, fetch it
        if not project_data["metadata"].get("project_slug"): fetch_ids.append(project_id)

    if fetch_ids != []:
        projects = json.loads(request(f"{modrinth_base_api}/v2/projects", query={
            "ids": json.dumps(fetch_ids)
        })["body"])

        for project in projects:
            if resolved_data[project["id"]]["relationship"]["type"] in (version_dependency_types["required"], version_dependency_types["incompatible"]):
                slug_id[project["slug"]] = {
                    "id": project["id"]
                }

            project_metadata = resolved_data[project["id"]]["metadata"]

            project_metadata["project_slug"] = project["slug"]
            project_metadata["project_title"] = project["title"]
            project_metadata["project_description"] = project["description"]
            project_metadata["project_license"] = project["license"]
            project_metadata["loaders"] = project["loaders"]

        # Update with new slug to ID data
        slug_id_file.write_text(json.dumps(slug_id, indent=2))

    # Write project index
    for project_id, project_data in resolved_data.items():
        project_type = project_data["relationship"]["type"]
        if project_type in (version_dependency_types["required"], version_dependency_types["incompatible"]):
            log.debug(f"Indexing project '{project_id}' with type {project_type} and manual {project_data["relationship"]['manual']}")
            #write_project_index(project_id, project_data)
            if project_index_exists(project_id):
                update_project_index(project_id, project_data["metadata"], project_data["relationship"])
            else:
                create_project_index(project_id, project_data["metadata"], project_data["relationship"])

    if debug_mode: print(json.dumps(resolved_data, indent=2))
    return resolved_data

#Command Functions
def add_projects(args):
    projects = args.projects

    if is_active():
        log.error(f"There's another MCServer processes running with process ID: {get_state()["process_id"]}")
        return 1

    server_config = load_config("server")
    server_loader = server_config["loader"]

    loader_name = server_loader["name"]
    server_version = server_config["version"]

    if server_loader["name"] == "vanilla":
        log.error("Vanilla Minecraft server does not support mod")
        return 1

    set_loader_context(loader_name)

    resolved_data = resolve_projects(projects, server_version, loader_name)

    # Get project IDs
    total_size = 0

    required_project_name = []
    optional_project_name = []
    incompatible_project_name = []

    for project in resolved_data.values():
        project_type = project["relationship"]["type"]
        if project_type == version_dependency_types["required"]:
            project_file = project["metadata"]["file"]
            if (loader_dir / project_file["filename"]).exists(): continue

            total_size += project_file["file_size"]
            required_project_name.append(f"{project["metadata"]['project_title']} ({project["metadata"]['project_slug']})")
        elif project_type == version_dependency_types["optional"]:
            optional_project_name.append(f"{project["metadata"]['project_title']} ({project["metadata"]['project_slug']})")
        elif project_type == version_dependency_types["incompatible"]:
            incompatible_project_name.append(f"{project["metadata"]['project_title']} ({project["metadata"]['project_slug']})")

    if required_project_name:
        required_project_count = len(required_project_name)
        log.info(f"{required_project_count} {pluralize(project_label, required_project_count)} that {pluralize('is', required_project_count)} going to be downloaded:")
        print(wrap_ansi(wrap_string(", ".join(required_project_name), initial_indent="    ", subsequent_indent="    "), "green"), end="\n\n")

    if optional_project_name:
        optional_project_count = len(optional_project_name)
        log.info(f"{optional_project_count} {pluralize(project_label, optional_project_count)} that {pluralize('is', optional_project_count)} optional:")
        print(wrap_ansi(wrap_string(", ".join(optional_project_name), initial_indent="    ", subsequent_indent="    "), "yellow"), end="\n\n")

    if incompatible_project_name:
        incompatible_project_count = len(incompatible_project_name)
        log.warning(f"{incompatible_project_count} {pluralize(project_label, incompatible_project_count)} that {pluralize('is', incompatible_project_count)} INCOMPATIBLE:")
        print(wrap_ansi(wrap_string(", ".join(incompatible_project_name), initial_indent=" ", subsequent_indent=" "), "red"), end="\n\n")

    if required_project_name:
        project_count = len(resolved_data)
        log.info(f"Will download {format_number(total_size, 'iec')} worth of {pluralize(project_label, project_count)} {pluralize("file", project_count)}.")
    else:
        log.info(f"All requested {pluralize(project_label, len(projects))} has been downloaded, nothing to do!")
        return 0

    answer = confirmation_prompt("Do you want to continue?", True)
    if not answer:
        print("Cancelled")
        return 1

    if not loader_dir:
        log.error("Cannot create directory for non-defined project type")
        return 1

    set_state("adding_project")

    loader_dir.mkdir(exist_ok=True)
    for project in resolved_data.values():
        if project["relationship"]["type"] == version_dependency_types["required"]:
            project_file = project["metadata"]["file"]
            if (loader_dir / project_file["filename"]).exists(): continue

            log.info(f"Downloading version {project["metadata"]['version_name']}...")
            download(project_file["url"], loader_dir / project_file["filename"], hashes=project_file["hashes"])

def initialize_server(args):
    # Arguments
    game_version = args.mc_version

    loader_name = args.loader
    loader_version = args.loader_version

    min_ram = args.min_ram
    max_ram = args.max_ram

    if loader_name == "vanilla":
        loader_version = None

    # Update project 'context'
    set_loader_context(loader_name)

    is_first_initialize = not metadata_file.exists()

    # Special latest game_version
    match game_version:
        case "latest" | "latest-release":
            latest_release_version = mojang.manifest.get_latest_release_version()
            log.info(f"Latest Minecraft release version is: {latest_release_version}")
            game_version = latest_release_version
        case "latest-snapshot":
            latest_snapshot_version = mojang.manifest.get_latest_snapshot_version()
            log.info(f"Latest Minecraft snapshot version is: {latest_snapshot_version}")
            game_version = latest_snapshot_version

    # Special latest loader_version
    if loader_version == "latest":
        match loader_name:
            # Mod loaders
            case "fabric":
                latest_loader_version = ""
                for version in fabricmc.meta.get_loader_versions():
                    if version["is_stable"]:
                        latest_loader_version = version["loader_version"]
                        break

                log.info(f"Latest Fabric Loader version is {latest_loader_version}")
                loader_version = latest_loader_version

            # Plugin loaders
            case "paper":
                latest_build_version = papermc.api.get_latest_project_build("paper", game_version)["build_version"]
                log.info(f"Latest Paper build version is: {latest_build_version}")
                loader_version = latest_build_version
            case "purpur":
                latest_build_version = purpurmc.api.get_latest_project_build("purpur", game_version)["build_version"]
                log.info(f"Latest Purpur build version is: {latest_build_version}")
                loader_version = latest_build_version

    # Creating the directories
    mcserver_dir.mkdir(exist_ok=True)
    configs_dir.mkdir(exist_ok=True)
    indexes_dir.mkdir(exist_ok=True)

    tempfiles_dir.mkdir(exist_ok=True)

    if loader_dir is not None:
        loader_dir.mkdir(exist_ok=True)

    # Creating the files
    if not slug_id_file.exists():
        slug_id_file.write_text(json.dumps({}, indent=2))

    # Generate configuration files
    for config_name in default_configs.keys():
        update_config = None
        match config_name:
            case "launcher":
                update_config = {
                    "ram": {
                        "min": min_ram,
                        "max": max_ram
                    }
                }

            case "server":
                update_config = {
                    "version": game_version,
                    "loader": {
                        "name": loader_name,
                        "version": loader_version
                    }
                }

        try:
            generate_config(config_name, update_config)
        except FileExistsError:
            log.debug(f"Configuration file '{config_name}' already exist, continuing...")

    if is_first_initialize:
        metadata_file.write_text(json.dumps({
            "mcserver": {
                "version": __version__
            }
        }, indent=2))

        log.info("Initialized server configuration.")
    else:
        log.info("Reinitialized server configuration.")

    return 0

def import_setup(args):
    file = Path(args.file)

    min_ram = args.min_ram
    max_ram = args.max_ram

    modpack_index = modrinth.modpack.read_index(file)

    loader_name = ""
    loader_version = ""
    for dependency_name, dependency_version in modpack_index["dependencies"].items():
        match dependency_name:
            case "minecraft":
                continue
            case "fabric-loader":
                loader_name = "fabric"
                loader_version = dependency_version
                break
            case _:
                log.error(f"Loader '{dependency_name}' is not supported")
                return 1

    args = argparse.Namespace(
        mc_version = modpack_index["dependencies"]["minecraft"],
        loader = loader_name,
        loader_version = loader_version,
        min_ram = min_ram,
        max_ram = max_ram
    )

    initialize_server(args)

    # Downloading files
    for file in modpack_index["files"]:
        mod_environment = file.get("mod_environment")

        if mod_environment is not None:
            match mod_environment["server_side"]:
                case "unsupported":
                    log.debug(f"Ignoring '{file['file_path']}', server is unsupported")
                    continue
                case "optional":
                    pass

def list_projects(args) -> int:
    return 0

# 'op' commands
def op_grant(args) -> int:
    players = args.players
    permission_level = args.permission_level
    bypasses_player_limit = args.bypasses_player_limit
    return 0

def op_list(args) -> int:
    return 0

def op_revoke(args) -> int:
    players = args.players
    return 0

def search_projects(args):
    query = " ".join(args.query)
    no_filter = args.no_filter

    page = args.page
    sort_by = args.sort_by

    modrinth_config = load_config("modrinth", allow_missing=True)
    search_limit = modrinth_config["search_limit"]

    search_index = sort_by or modrinth_config.get("sort_by", "relevance")
    search_offset = search_limit * (page - 1)
    search_message = f"Searching projects with '{query}' in Modrinth sorted by {search_index}..."
    search_filters = []

    if not (configs_dir / "server.json").exists():
        log.warning("Configuration file for 'server' is missing, no version filter will be applied.")

        search_filters = []
        search_message = f"Searching projects with '{query}' in Modrinth sorted by {search_index}..."
    elif not no_filter:
        server_config = load_config("server")
        server_loader = server_config["loader"]

        server_version = server_config["version"]
        loader_name = server_loader["name"]

        set_loader_context(loader_name)

        if loader_name == "vanilla":
            raise SearchProjectsError("Vanilla Minecraft server does not support mod.")

        search_message = f"Searching {pluralize(project_label)} with '{query}' in Modrinth for {loader_name.capitalize()}, Minecraft server {server_version} sorted by {search_index}..."
        search_filters = [
            [f"project_type:{project_label}"],
            ["server_side!=unsupported"],
            [f"categories:{loader_name}"],
            [f"versions:{server_version}"]
        ]

    log.info(search_message)
    response = json.loads(request(f"{modrinth_base_api}/v2/search", query={
            "query": query,
            "facets": json.dumps(search_filters),
            "index": search_index,
            "limit": search_limit,
            "offset": search_offset
        })["body"])

    projects_list = response.get("hits", [])
    if not projects_list:
        log.error(f"No {project_label} found.")
        return 1

    server_side_width = 0
    client_side_width = 0

    downloads_width = 0
    follows_width = 0

    for project in projects_list:
        server_side_width = max(server_side_width, len(project.get("server_side", "unknown")))
        client_side_width = max(client_side_width, len(project.get("client_side", "unknown")))

        downloads = project.get("downloads", 0)
        downloads_width = max(downloads_width, len(f"{pluralize('Download', downloads)}: {format_number(downloads)}"))

        follows = project.get("follows", 0)
        follows_width = max(follows_width, len(f"{pluralize('Follow', follows)}: {format_number(follows)}"))

    total_hits = response.get("total_hits", 0)
    total_pages = f"{math.ceil(total_hits / search_limit):,}"

    response_offset = response.get("offset", 0)
    shown_projects_count = min(len(projects_list), search_limit)

    skipped_message = f"(skipped {response_offset:,} {pluralize(project_label, response_offset)}) " if response_offset > 0 else ""
    log.info(f"Showing {shown_projects_count:,} {pluralize(project_label, shown_projects_count)} out of {total_hits:,} total {pluralize(project_label, total_hits)} {skipped_message}| Page: {page:,}/{total_pages}")

    for index, project in enumerate(projects_list):
        title = wrap_ansi(project.get("title", "<No Title>"), "bold")
        slug = project.get("slug", "<No Slug>")
        author = f"by {project.get('author', '<No Author>')}"

        project_header = wrap_string(f"{title} ({slug}) {wrap_ansi(author, 'gray')}", subsequent_indent=" ")

        downloads = project.get("downloads", 0)
        follows = project.get("follows", 0)

        downloads_text = f"{pluralize('Download', downloads)}: {format_number(downloads)}"
        follows_text = f"{pluralize('Follow', follows)}: {format_number(follows)}"
        downloads_follows = wrap_ansi(f"[ {downloads_text: <{downloads_width}} | {follows_text: <{follows_width}} ]", "gray")

        server_side = wrap_ansi(f"Server: {mod_environment_color(project.get('server_side', "unknown"), server_side_width)}", "bold")
        client_side = mod_environment_color(project.get("client_side", "unknown"), client_side_width)

        description = wrap_string(project["description"], initial_indent="    ", subsequent_indent=" ")

        is_end_of_list = (index + 1) == shown_projects_count

        print(f"""{project_header}
[ {server_side} | Client: {client_side} ] {downloads_follows}
> https://modrinth.com/{project_label}/{slug}
{description}""", end="\n" if is_end_of_list else "\n\n")

def show_projects(args):
    projects = args.projects

    set_loader_context(load_config("server", allow_missing=True)["loader"]["name"])

    log.info(f"Getting {pluralize(project_label, len(projects))} information...")
    projects_info = json.loads(request(f"{modrinth_base_api}/v2/projects", query={
            "ids": json.dumps(projects)
        }
    )["body"])

    for project_index, project in enumerate(projects_info):
        title = wrap_ansi(project.get("title", "") or "<No Title>", "bold")
        slug = wrap_ansi(project.get("slug", f"<{projects[project_index]}>"), "bold")

        downloads = wrap_ansi(format_number(project.get("downloads", 0)), "bold")
        followers = wrap_ansi(format_number(project.get("followers", 0)), "bold")

        project_categories = ', '.join(project.get('categories', ['None'])).title()
        categories = wrap_string(f"Categories: {wrap_ansi(project_categories, 'bold')}", subsequent_indent=" ")

        project_loaders = ', '.join(project.get('loaders', ['None'])).title()
        loaders = wrap_string(f"Loaders: {wrap_ansi(project_loaders, 'bold')}", subsequent_indent=" ")

        project_game_versions = ', '.join(project.get('game_versions', ['None'])).title()
        game_versions = wrap_string(f"Minecraft Versions: {wrap_ansi(project_game_versions, 'bold')}", subsequent_indent=" ")

        server_side = wrap_ansi(f"Server: {mod_environment_color(project.get('server_side', '<Unknown>'))}", "bold")
        client_side = mod_environment_color(project.get("client_side", "<Unknown>"))

        project_license = project.get("license", {})
        license_name = wrap_ansi(project_license.get("name", "") or "All Rights Reserved", "bold")
        license_id = wrap_ansi(project_license.get("id", "") or "LicenseRef-All-Rights-Reserved", "bold")

        project_homepage = project.get("slug", project["id"])
        homepage = wrap_ansi(f"https://modrinth.com/{project_label}/{project_homepage}", "bold")

        project_description = project.get('description', '<No Description>')
        description = wrap_string(f"Description: {wrap_ansi(project_description, 'bold')}", subsequent_indent=" ")

        if (project_index >= 1): print()
        print(f"""Name: {title} ({slug})
Downloads: {downloads}
Followers: {followers}
{categories}
{loaders}
{game_versions}
Environment: {server_side} | Client: {client_side}
License: {license_name} ({license_id})
Homepage: {homepage}
{description}""")

def start_server(args):
    # Checking current state
    if state.is_active():
        current_state = state.get_state()
        log.error(f"There's another active MCServer process ({current_state["action"]}) running with process ID: {current_state["process_id"]}")
        return 1

    state.set_state("running_server")

    # Loading configs
    server_config = config.load_config("server")
    launcher_config = config.load_config("launcher")

    server_loader = server_config["loader"]
    game_version = server_config["version"]

    loader_name = server_loader["name"]
    loader_version = server_loader["version"]

    jarfile = launcher_config["jarfile"]
    memory_config = launcher_config["ram"]

    # Download jarfile
    if not Path(jarfile).exists():
        match loader_name:
            # Mod loaders
            case "fabric":
                log.info(f"Downloading Fabric loader {loader_version} for Minecraft version {game_version}...")
                networking.download(f"https://meta.fabricmc.net/v2/versions/loader/{game_version}/{loader_version}/1.1.1/server/jar", launcher_config["jarfile"])

            # Plugin loaders
            case "paper":
                log.info(f"Downloading Paper version {loader_version} for Minecraft version {game_version}...")
                download_prop = papermc.api.get_project_build("paper", game_version, loader_version)["download_props"]["server:default"]
                networking.download(download_prop["download_url"], launcher_config["jarfile"], dict(download_prop["checksums"]))
            case "purpur":
                log.info(f"Downloading Purpur version {loader_version} for Minecraft version {game_version}...")
                networking.download(purpurmc.api.download_url("purpur", game_version, loader_version), launcher_config["jarfile"], {
                    "md5": purpurmc.api.get_project_build("purpur", game_version, loader_version)["artifact_md5"]
                })

            # Vanilla
            case "vanilla":
                log.debug("Getting Mojang version manifest file...")
                version_manifest = mojang.manifest.get_version_manifest()["game_versions"]

                selected_version_url = None
                for version in version_manifest:
                    if version["version_id"] == game_version:
                        selected_version_url =    version["package_url"]
                        break

                if selected_version_url is None:
                    log.error(f"Minecraft version {game_version} is not found.")
                    return 1

                server_download = json.loads(networking.request(selected_version_url)["body"])["downloads"]["server"]
                log.info(f"Downloading vanilla Minecraft version {game_version}...")

                networking.download(server_download["url"], launcher_config["jarfile"], {
                    "sha1": server_download["sha1"]
                })
            
            case _:
                log.error(f"Loader '{loader_name}' is not supported.")
                return 1

    # Running the server
    if not shutil.which("java"):
        log.error("Cannot find 'java' in PATH, is Java Runtime Environment installed correctly?")
        return 1

    if memory_config["min"] > memory_config["max"]:
        log.error(f"Minimum RAM cannot be larger that maximum RAM, please check configuration for `launcher`")
        return 1

    #TODO: Implement the "free RAM" checker here

    try:
        if not mojang.eula.is_eula_agreed():
            log.warning("You need to agree to Mojang's EULA in order to run the server: https://aka.ms/MinecraftEULA")
            log.info(f"Please type '{wrap_ansi(eula_agree_sentence, 'yellow')}' (case-insensitive) to agree with Mojang's EULA.")
            answer = input("> ")

            if answer.lower().strip() == eula_agree_sentence.lower().strip():
                mojang.eula.eula_agree()
            else:
                log.error("Failed to start the Minecraft server: EULA not agreed")
                return 1
    except KeyboardInterrupt:
        log.error("\nFailed to start the Minecraft server: EULA not agreed")
        return 1

    java_command_argv = [
        "java",
        f"-Xmx{memory_config['max']}M",
        f"-Xms{memory_config['min']}M",
        "-jar",
        launcher_config["jarfile"]
    ]

    if launcher_config["hide_gui"]:
        java_command_argv.append("nogui")

    log.info("Starting Minecraft server...")

    log.debug(f"Executing command: {' '.join(java_command_argv)}")
    os.execvp(java_command_argv[0], java_command_argv)

def whitelist_add(args) -> int:
    players = args.players
    return 0

def whitelist_list(args) -> int:
    return 0

def whitelist_remove(args) -> int:
    players = args.players
    return 0

#Log handler
class ClearLineHandler(log.StreamHandler):
    def emit(self, record):
        self.stream.write(ansi('clear_line') + ansi('start_line'))
        self.stream.flush()
        super().emit(record)

#Main
def main():
    if ((sys.argv[1] if len(sys.argv) > 1 else "") == "cake"): hahaha_yes()

    log_handler = ClearLineHandler(sys.stdout)
    log_handler.setFormatter(log.Formatter("[%(levelname)s]: %(message)s"))

    log.basicConfig(
        level=log_level,
        handlers=[log_handler]
    )

    # Parser
    parser = argparse.ArgumentParser(
        prog="mcserver",
        description="A CLI tool for managing Minecraft: Java Edition servers.",
        epilog="Not created for Windows.",
        allow_abbrev=False,
        suggest_on_error=True,
        color=True)

    parser.set_defaults(func=print_help, parser=parser)

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s " + __version__)

    commands = parser.add_subparsers(title="Commands")

    #Commands
    # 'add' command
    add_command = commands.add_parser("add", help="Add Modrinth projects", description="Add Modrinth projects")
    add_command.set_defaults(func=add_projects)

    add_command.add_argument("projects", nargs="+", type=str, help="Project slugs or IDs")

    # 'import' command
    import_command = commands.add_parser("import", description="Import a Modrinth modpack", help="Import a Modrinth modpack")
    import_command.set_defaults(func=import_setup)

    import_command.add_argument("file", type=str, help="Modpack file")
    import_command.add_argument("--min-ram", default=512, type=int, help="Minimum RAM for the server (in Mebibytes)", metavar="size")
    import_command.add_argument("--max-ram", default=2048, type=int, help="Maximum RAM for the server (in Mebibytes)", metavar="size")

    # 'init' command
    init_command = commands.add_parser("init", help="Initialize server configurations")
    init_command.set_defaults(func=initialize_server)

    init_command.add_argument("--mc-version", default="latest-release", type=str, help="Minecraft server version", metavar="version")
    init_command.add_argument("--loader", default="vanilla", type=str, choices=loaders_list, help="Loader for the server (vanilla for unmodded server)")
    init_command.add_argument("--loader-version", default="latest", type=str, help="Version of the loader", metavar="version")
    init_command.add_argument("--min-ram", default=512, type=int, help="Minimum RAM for the server (in Mebibyte)", metavar="size")
    init_command.add_argument("--max-ram", default=2048, type=int, help="Maximum RAM for the server (in Mebibyte)", metavar="size")

    # 'list' command
    list_command = commands.add_parser("list", description="List downloaded projects", help="List downloaded projects")
    list_command.set_defaults(func=list_projects)

    # 'op' commands
    op_command = commands.add_parser("op", help="Manage operator statuses", description="Manage operator statuses")
    op_command.set_defaults(func=print_help, parser=op_command)

    op_subcommands = op_command.add_subparsers(title="Subcommands")

    # 'op grant'
    op_grant_command = op_subcommands.add_parser("grant", help="Grant operator status to players", description="Grant operator status to players")
    op_grant_command.set_defaults(func=op_grant)

    op_grant_command.add_argument("players", nargs="+", help="Player names or UUIDs")
    op_grant_command.add_argument("--level", type=int, choices=[0, 1, 2, 3 4], help="Operator permission level (0-4)", metavar="level", dest="permission_level")
    op_grant_command.add_argument("--bypass-player-limit", action="store_true", help="Can bypass player limit", dest="bypasses_player_limit")

    # 'op list'
    op_list_command = op_subcommands.add_parser("list", help="List all operators", description="List all operators")
    op_list_command.set_defaults(func=op_list)

    # 'op revoke'
    op_revoke_command = op_subcommands.add_parser("revoke", help="Revoke operator status from players", description="Revoke operator status from players")
    op_revoke_command.set_defaults(func=op_revoke)

    op_revoke_command.add_argument("players", nargs="+", help="Player names or UUIDs")

    # 'search' command
    search_command = commands.add_parser("search", help="Search Modrinth projects", description="Search Modrinth projects")
    search_command.set_defaults(func=search_projects)

    search_command.add_argument("query", nargs="*", type=str, help="Search query")
    search_command.add_argument("-n", "--no-filter", action="store_true", help="No search filter from server configuration")
    search_command.add_argument("-p", "--page", default=1, type=int, help="Page number", metavar="N")
    search_command.add_argument("-s", "--sort-by", default="relevance", type=str, choices=["downloads", "follows", "newest", "relevance", "updated"], help="Sort search result by")

    # 'show' command
    show_command = commands.add_parser("show", help="Show project information", description="Show project information")
    show_command.set_defaults(func=show_projects)

    show_command.add_argument("projects", nargs="+", type=str, help="Project slugs or IDs")

    # 'start' command
    start_command = commands.add_parser("start", description="Start the server", help="Start the server")
    start_command.set_defaults(func=start_server)

    # 'whitelist' command
    whitelist_command = commands.add_parser("whitelist", help="Manage whitelisted players", description="Manage whitelisted players")
    whitelist_command.set_defaults(func=print_help, parser=whitelist_command)

    whitelist_subcommands = whitelist_command.add_subparsers(title="Subcommands")

    # 'whitelist add'
    whitelist_add_command = whitelist_subcommands.add_parser("add", help="Add players to the whitelist", description="Add players to the whitelist")
    whitelist_add_command.set_defaults(func=whitelist_add)

    whitelist_add_command.add_argument("players", nargs="+", help="Player names or UUIDs")

    # 'whitelist list'
    whitelist_list_command = whitelist_subcommands.add_parser("list", help="List all whitelisted players", description="List all whitelisted players")
    whitelist_list_command.set_defaults(func=whitelist_list)

    # 'whitelist remove'
    whitelist_remove_command = whitelist_subcommands.add_parser("remove", help="Remove players from the whitelist", description="Remove players from the whitelist")
    whitelist_remove_command.set_defaults(func=whitelist_remove)

    whitelist_remove_command.add_argument("players", nargs="+", help="Player names or UUIDs")

    args = parser.parse_args()
    sys.exit(args.func(args))

### This file used to be a one big script file, like 1,200 lines of codes.
### and the modularization happens after I found out about zipapp, silly me.
### The reason that I might "reinvent the wheel" is because I used to want it just
### download script and run without the 'pip install -r requirements.txt' ritual
### and that is way before I knew about zipapp, so I can't bundle requests or
### something. blBut now? I technically can, but I'll just continue the
### dependency-free code, for fun and learning :shrug:. that means 100% of the
### projectis written by me. yep, absolutely every bit of this prpject, no
### external code at all!
