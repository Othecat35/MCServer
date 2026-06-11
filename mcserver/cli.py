import argparse, json, math, os, shutil, sys, textwrap, time
import logging as log

from config import default_configs, generate_config, load_config
from constants import __version__
from indexing import project_index_exists, write_project_index, read_project_index, project_indexes_dir, slug_to_id, slug_id_file, slug_id
from modrinth_api import get_project_versions, ProjectVersionDependency, modrinth_base_api
from network import download_url, request_url
from shared import ansi, mcserver_dir, mod_environment_color, pluralize, format_number, wrap_ansi, confirmation_prompt

from pathlib import Path
from collections import deque

# Variables
debug_mode = os.getenv("MCSERVER_DEBUG") == "1"
log_level = log.DEBUG if debug_mode else log.INFO

mods_loader = ["fabric"]
plugins_loader = ["paper"]
loaders_list = ["vanilla"] + mods_loader + plugins_loader

eula_agree_sentence = "Yes, I agree."

# Severity levels
version_dependency_types = {
  "embedded": 0,
  "optional": 1,
  "required": 2,
  "incompatible": 3
}

# Paths
mods_dir = Path("mods")
plugins_dir = Path("plugins")

configs_dir = mcserver_dir / "configs"
tempfiles_dir = mcserver_dir / "tempfiles"

# Error classes
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

# Functions
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
project_dir = None

def update_project_label(loader_name: str):
  global project_label
  global project_dir

  if loader_name in mods_loader:
    project_label = "mod"
    project_dir = mods_dir
  elif loader_name in plugins_loader:
    project_label = "plugin"
    project_dir = plugins_dir

# Resolve prejects dependencies
def adapt_dependencies_data(dependencies: list[ProjectVersionDependency]) -> dict:
  dependencies_data = {}
  for dependency in dependencies:
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
      "manual": True,
      "type": version_dependency_types["required"],
      "dependants": {}
    }

  # Main code
  while unresolved_ids:
    project_id = unresolved_ids.popleft()
    project_data = resolved_data.pop(project_id)

    log.debug(f"Processing project '{project_id}'")

    skip_fetch_version = False

    if project_index_exists(project_id):
      project_index_data = read_project_index(project_id)
      project_index_type = project_index_data["type"]

      if project_index_type == version_dependency_types["incompatible"]:
        project_index_dependants = project_index_data["dependants"]

        incompatible_dependants = filter_dependencies_type(project_index_dependants, "incompatible")
        required_dependants = filter_dependencies_type(project_index_dependants, "required")
        raise ResolveProjectsConflictsError(project_id, incompatible_dependants, required_dependants)

      log.debug("Project index exists, using it as cache")
      project_index_data["dependants"].update(project_data["dependants"])
      if project_data["manual"]:
        project_index_data["manual"] = True

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

        # Check if existing entry is marked as incompatible
        if existing_entry["type"] == version_dependency_types["incompatible"]:
          incompatible_dependants = filter_dependencies_type(existing_entry["dependants"], "incompatible")
          raise ResolveProjectsConflictsError(project_id, incompatible_dependants)

        log.debug(f"Keeping existing data")
        project_data["dependants"].update(existing_entry["dependants"])

      project_data["version_id"] = version["version_id"]
      project_data["version_name"] = version["version_name"]
      project_data["version_number"] = version["version_number"]

      project_data["dependencies"] = adapt_dependencies_data(version["dependencies"])
      project_data["file"] = version["primary_file"]

    for dependency_id, dependency_type in project_data["dependencies"].items():
      if dependency_id in resolved_data:
        dependency_data = resolved_data[dependency_id]
        dependency_data_type = dependency_data["type"]
        dependency_data_dependants = dependency_data["dependants"]

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
        dependency_data["dependants"][project_id] = dependency_type
        dependency_data["type"] = max(dependency_data["type"], dependency_type)
      else:
        log.debug(f"Adding new project entry for dependency: {dependency_id}")
        resolved_data[dependency_id] = {
          "manual": False,
          "type": dependency_type,
          "dependants": {
            project_id: dependency_type
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
    if not project_data.get("slug"): fetch_ids.append(project_id)

  projects = json.loads(request_url(f"{modrinth_base_api}/projects", query={
    "ids": json.dumps(fetch_ids)
  })["body"])

  for project in projects:
    if resolved_data[project["id"]]["type"] in (version_dependency_types["required"], version_dependency_types["incompatible"]):
      slug_id[project["slug"]] = {
        "id": project["id"]
      }

    project_data = resolved_data[project["id"]]

    project_data["project_slug"] = project["slug"]
    project_data["project_title"] = project["title"]
    project_data["project_description"] = project["description"]
    project_data["project_license"] = project["license"]
    project_data["loaders"] = project["loaders"]

  # Update with new slug to ID data
  slug_id_file.write_text(json.dumps(slug_id, indent=2))

  # Write project index
  for project_id, project_data in resolved_data.items():
    project_type = project_data["type"]
    if project_type in (version_dependency_types["required"], version_dependency_types["incompatible"]):
      log.debug(f"Indexing project '{project_id}' with type {project_type} and manual {project_data['manual']}")
      write_project_index(project_id, project_data)

  if debug_mode: print(json.dumps(resolved_data, indent=2))
  return resolved_data

# EULA functions
def check_eula_agreed():
  try:
    with open("eula.txt") as file:
      for line in file.readlines():
        if line.startswith("eula=true"):
          return True
  except FileNotFoundError:
    pass

  return False

def eula_agree():
  timestamp = time.strftime("%a %b %d %H:%M:%S GMT %Y", time.gmtime())
  with open("eula.txt", mode="wt") as file:
    file.write(f"""#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://aka.ms/MinecraftEULA).
#{timestamp}
eula=true""")

# Command functions
def add_projects(args):
  projects = args.projects

  server_config = load_config("server")
  server_loader = server_config["loader"]

  loader_name = server_loader["name"]
  server_version = server_config["version"]

  if server_loader["name"] == "vanilla":
    log.error("Vanilla Minecraft server does not support mod")
    return 1

  update_project_label(loader_name)

  resolved_data = resolve_projects(projects, server_version, loader_name)

  # Get project IDs
  total_size = 0

  required_project_name = []
  optional_project_name = []
  incompatible_project_name = []

  for project in resolved_data.values():
    project_type = project["type"]
    if project_type == version_dependency_types["required"]:
      project_file = project["file"]
      if (project_dir / project_file["filename"]).exists(): continue

      total_size += project_file["file_size"]
      required_project_name.append(f"{project['project_title']} ({project['project_slug']})")
    elif project_type == version_dependency_types["optional"]:
      optional_project_name.append(f"{project['project_title']} ({project['project_slug']})")
    elif project_type == version_dependency_types["incompatible"]:
      incompatible_project_name.append(f"{project['project_title']} ({project['project_slug']})")

  if required_project_name:
    required_project_count = len(required_project_name)
    log.info(f"{required_project_count} {pluralize(project_label, required_project_count)} that {pluralize('is', required_project_count)} going to be downloaded:")
    print(wrap_ansi(wrap_string(", ".join(required_project_name), initial_indent="  ", subsequent_indent="  "), "green"), end="\n\n")

  if optional_project_name:
    optional_project_count = len(optional_project_name)
    log.info(f"{optional_project_count} {pluralize(project_label, optional_project_count)} that {pluralize('is', optional_project_count)} optional:")
    print(wrap_ansi(wrap_string(", ".join(optional_project_name), initial_indent="  ", subsequent_indent="  "), "yellow"), end="\n\n")

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

  if not project_dir:
    log.error("Cannot create directory for non-defined project type")
    return 1

  project_dir.mkdir(exist_ok=True)
  for project in resolved_data.values():
    if project["type"] == version_dependency_types["required"]:
      project_file = project["file"]
      if (project_dir / project_file["filename"]).exists(): continue

      log.info(f"Downloading version {project['version_name']}...")
      download_url(project_file["url"], project_dir / project_file["filename"], hashes=project_file["hashes"])

def initialize_server(args):
  mc_version = args.mc_version

  loader = args.loader
  loader_version = args.loader_version

  min_ram = args.min_ram
  max_ram = args.max_ram

  if not mcserver_dir.exists():
    log.info(f"Initializing server configuration...")
  else:
    log.info(f"Reinitializing server configuration...")

  update_project_label(loader)

  mcserver_dir.mkdir(exist_ok=True)

  configs_dir.mkdir(exist_ok=True)
  project_indexes_dir.mkdir(exist_ok=True)

  tempfiles_dir.mkdir(exist_ok=True)

  if not slug_id_file.exists():
    slug_id_file.write_text(json.dumps({}, indent=2))

  if mc_version == "latest":
    log.info("Getting Mojang game version manifest...")
    latest_version = json.loads(request_url("https://launchermeta.mojang.com/mc/game/version_manifest.json")["body"])["latest"]["release"]
    mc_version = latest_version

  if loader == "vanilla":
    loader_version = None

  # TODO: add the "latest" for loader version too

  if project_dir is not None:
    project_dir.mkdir(exist_ok=True)

  update_values = None
  for config in default_configs.keys():
    if config == "launcher":
      update_values = {
        "ram": {
          "min": min_ram,
          "max": max_ram
        }
      }

    if config == "server":
      update_values = {
        "version": mc_version,
        "loader": {
          "name": loader,
          "version": loader_version
        }
      }

    try:
      generate_config(config, update_config=update_values)
    except FileExistsError:
      log.debug(f"Configuration file for `{config}` already exists, not regenerating")

def install_server(args):
  server_config = load_config("server")
  launcher_config = load_config("launcher")

  server_loader = server_config["loader"]
  server_version = server_config["version"]

  loader_name = server_loader["name"]
  loader_version = server_loader["version"]

  match loader_name:
    case "fabric":
      log.info(f"Downloading Fabric loader {loader_version} for Minecraft server {server_version}...")
      download_url(f"https://meta.fabricmc.net/v2/versions/loader/{server_version}/{loader_version}/1.1.1/server/jar", launcher_config["jarfile"])
    case "vanilla":
      log.info("Getting Mojang game version manifest...")
      version_manifest = json.loads(request_url("https://launchermeta.mojang.com/mc/game/version_manifest.json")["body"])

      selected_version_url = ""
      for version in version_manifest["versions"]:
        if version["id"] == server_version:
          selected_version_url =  version["url"]
          break

      server_download = json.loads(request_url(selected_version_url)["body"])["downloads"]["server"]
      log.info(f"Downloading jarfile for vanilla Minecraft server {server_version}...")

      download_url(server_download["url"], launcher_config["jarfile"], hashes={
        "sha1": server_download["sha1"]
      })
    case _:
      raise InstallServerError(f"Server loader '{loader_name}' is not supported")

  log.info("Server installation is complete.")

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

    update_project_label(loader_name)

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
  response = json.loads(request_url(f"{modrinth_base_api}/search", query={
      "query": query,
      "facets": json.dumps(search_filters),
      "index": search_index,
      "limit": search_limit,
      "offset": search_offset
    })["body"])

  projects_list = response.get("hits", [])
  if not projects_list:
    raise SearchProjectsError(f"No mod found.")

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

    description = wrap_string(project["description"], initial_indent="  ", subsequent_indent=" ")

    is_end_of_list = (index + 1) == shown_projects_count

    print(f"""{project_header}
[ {server_side} | Client: {client_side} ] {downloads_follows}
> https://modrinth.com/mod/{slug}
{description}""", end="\n" if is_end_of_list else "\n\n")

def show_projects(args):
  projects = args.projects

  update_project_label(load_config("server", allow_missing=True)["loader"]["name"])

  log.info(f"Getting {pluralize(project_label, len(projects))} information...")
  projects_info = json.loads(request_url(f"{modrinth_base_api}/projects", query={
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
    homepage = wrap_ansi(f"https://modrinth.com/mod/{project_homepage}", "bold")

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
  launcher_config = load_config("launcher")
  memory_limit = launcher_config["ram"]

  jarfile = launcher_config['jarfile']

  if not Path(jarfile).exists():
    log.error(f"Couldn't find server jarfile '{jarfile}'")
    return 1

  if not shutil.which("java"):
    log.error("Cannot find 'java' in PATH, is Java installed correctly?")
    return 1

  if memory_limit["min"] > memory_limit["max"]:
    log.error(f"Minimum RAM cannot be larger that maximum RAM, please check configuration for `launcher`")
    return 1

  try:
    if not check_eula_agreed():
      log.warning("You need to agree to Mojang's EULA in order to run the server: https://aka.ms/MinecraftEULA")
      log.info(f"Please type '{wrap_ansi(eula_agree_sentence, 'yellow')}' (case-insensitive) to agree with Mojang's EULA.")
      answer = input("> ")

      if answer.lower() == eula_agree_sentence.lower():
        eula_agree()
      else:
        log.error("Failed to start the Minecraft server: EULA not agreed")
        return 1
  except KeyboardInterrupt:
    log.error("\nFailed to start the Minecraft server: EULA not agreed")
    return 1

  java_command_argv = [
    "java",
    f"-Xmx{memory_limit['max']}M",
    f"-Xms{memory_limit['min']}M",
    "-jar",
    launcher_config["jarfile"]
  ]

  if launcher_config["hide_gui"]:
    java_command_argv.append("nogui")

  log.info("Starting Minecraft server...")
  log.debug(f"Executing command: {' '.join(java_command_argv)}")
  os.execvp(java_command_argv[0], java_command_argv)

# Log handler
class ClearLineHandler(log.StreamHandler):
  def emit(self, record):
    self.stream.write(ansi('clear_line') + ansi('start_line'))
    self.stream.flush()
    super().emit(record)

# Main
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
    description="A CLI tool for managing a Minecraft: Java Edition server.",
    epilog="Not created for Windows.",
    allow_abbrev=False)

  parser.set_defaults(func=print_help, parser=parser)
  parser.add_argument(
    "-v", "--version",
    action="version",
    version="%(prog)s " + __version__)

  subparsers = parser.add_subparsers(title="Commands")

  #Setup
  # 'init' command
  parser_init = subparsers.add_parser("init", help="Initialize the server configurations")

  parser_init.add_argument("--mc-version", default="latest", type=str, help="Minecraft version of the server", metavar="version")

  parser_init.add_argument("--loader", default="vanilla", type=str, choices=loaders_list, help="Loader for the server (vanilla for unmodded server)")
  parser_init.add_argument("--loader-version", default="latest", type=str, help="Version of the loader", metavar="version")

  parser_init.add_argument("--min-ram", default=512, type=int, help="Minimum RAM for the server (in Mebibyte)", metavar="size")
  parser_init.add_argument("--max-ram", default=2048, type=int, help="Maximum RAM for the server (in Mebibyte)", metavar="size")
  parser_init.set_defaults(func=initialize_server)

  # 'install' command
  parser_install = subparsers.add_parser("install", description="Install the server", help="Install the server")
  parser_install.set_defaults(func=install_server)

  # 'start' command
  parser_start = subparsers.add_parser("start", description="Start the server", help="Start the server")
  parser_start.set_defaults(func=start_server)

  #Mod management
  # 'add' command
  parser_add = subparsers.add_parser("add", description="Add project(s) from Modrinth", help="Add project(s) from Modrinth")
  parser_add.add_argument("projects", nargs="+", type=str, help="Slug (or ID) of the project(s)")
  parser_add.set_defaults(func=add_projects)

  # 'search' command
  parser_search = subparsers.add_parser("search", description="Search projects in Modrinth", help="Search projects in Modrinth")
  parser_search.add_argument("query", nargs="*", type=str, help="Query to search")

  parser_search.add_argument("-n", "--no-filter", action="store_true", help="No search filter from server configuration")

  parser_search.add_argument("-p", "--page", default=1, type=int, help="Page number", metavar="N")
  parser_search.add_argument("-s", "--sort-by", default="relevance", type=str, choices=["downloads", "follows", "newest", "relevance", "updated"], help="Sort the search result")
  parser_search.set_defaults(func=search_projects)

  # 'show' command
  parser_show = subparsers.add_parser("show", description="Show information about project(s) in Modrinth", help="Show information about project(s) in Modrinth")
  parser_show.add_argument("projects", nargs="+", type=str, help="Slug (or ID) of the project(s)")
  parser_show.set_defaults(func=show_projects)

  args = parser.parse_args()
  sys.exit(args.func(args))
