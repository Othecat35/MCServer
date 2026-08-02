#Modules
from argparse import Namespace as argparseNamespace

#Fucntions
def add_projects(args: argparseNamespace) -> int:
    projects: list[str] = args.projects
    print(projects)
    return 0

def import_setup(args: argparseNamespace) -> int:
    return 0

def init_server(args: argparseNamespace) -> int:
    # CLI Arguments
    game_version: str = args.game_version

    loader_name: str = args.loader_name
    loader_version: str | None = args.loader_version

    min_ram: int = args.min_ram
    max_ram: int = args.max_ram

    # Imports
    import copy
    import logging as log

    from . import __version__
    from . import config
    from . import shared
    from . import state

    from .metadata import metadata_file
    from .metadata import set_metadata

    # Special loader version
    if loader_name == "vanilla":
        loader_version = None

    # Special latest game_version
    if game_version in ["latest", "latest-release", "latest-snapshot"]:
        from .mojang import manifest as mojang_manifest
        match game_version:
            case "latest" | "latest-release":
                game_version = mojang_manifest.get_latest_release_version()
                log.info(f"Latest Minecraft release version is: {game_version}")
            case "latest-snapshot":
                game_version = mojang_manifest.get_latest_snapshot_version()
                log.info(f"Latest Minecraft snapshot version is: {game_version}")

    # Special latest loader_version
    if loader_version == "latest":
        match loader_name:
            # Mod Loaders
            case "fabric":
                from .fabricmc import meta as fabricmc_meta
                loader_versions = fabricmc_meta.get_loader_versions()
                for version in loader_versions:
                    if version["is_stable"]:
                        loader_version = version["loader_version"]
                        break

                log.info(f"Latest Fabric loader version is {loader_version}")
            case "quilt":
                from .quiltmc import meta as quiltmc_meta
                loader_versions = quiltmc_meta.get_loader_versions()
                latest_quilt_version = loader_versions[0]
                loader_version = str(latest_quilt_version["loader_version"])
                log.info(f"Latest Quilt loader version is {loader_version}")
            # Plugin Loader
            case "paper":
                from .papermc import api as papermc_api
                latest_paper_version = papermc_api.get_latest_project_build("paper", game_version)
                loader_version = str(latest_paper_version["build_id"])
                log.info(f"Latest Paper build version is: {loader_version}")
            case "purpur":
                from .purpurmc import api as purpurmc_api
                latest_purpur_version = purpurmc_api.get_latest_project_build("purpur", game_version)
                loader_version = str(latest_purpur_version["build_id"])
                log.info(f"Latest Purpur build version is: {loader_version}")

            case _:
                log.error(f"Unknown loader: {loader_name}")
                return 1

    # Is first initializing
    is_first_initialize = not metadata_file.exists()
    shared.set_loader_context(loader_name)

    shared.mcserver_dir.mkdir(exist_ok=True)
    state.set_state("initializing_server")

    config.configs_dir.mkdir(exist_ok=True)
    shared.tempfiles_dir.mkdir(exist_ok=True)
    if shared.loader_context["project_directory"] is not None:
        shared.loader_context["project_directory"].mkdir(exist_ok=True)

    # Write configuration to file
    for config_name in shared.default_configs.keys():
        default_config = copy.deepcopy(shared.default_configs[config_name])

        config_override: dict = {}
        match config_name:
            case "launcher":
                config_override = {
                    "ram": {
                        "min": min_ram,
                        "max": max_ram
                    }
                }

            case "server":
                config_override = {
                    "game_version": game_version,
                    "loader": {
                        "name": loader_name,
                        "version": loader_version
                    }
                }

        config_data = shared.merge_dict(default_config, config_override)
        try:
            config.generate_config(config_name, config_data)
        except FileExistsError:
            log.debug(f"Configuration file {config_name} already exists")

    if is_first_initialize:
        set_metadata(__version__)
        log.info("Initialized server configurations.")
    else:
        log.info("Reinitialized server configurations.")

    return 0

def list_projects(args: argparseNamespace) -> int:
    return 0

# Operators
def op_grant(args: argparseNamespace) -> int:
    players: list[str] = args.players
    print(players)
    return 0

def op_list(args: argparseNamespace) -> int:
    import logging as log
    from .server_files import ops
    from .shared import pluralize

    if not ops.ops_file.exists():
        log.error(f"File '{ops.ops_file}' not found.")
        return 1

    operator_players = ops.list_players()

    players: list[str] = []
    for player in operator_players:
        players.append(f"{player['player_name']} ({player['player_uuid']}) Level: {player["permission_level"]}")

    players.sort()
    sorted_players = "\n".join(players)

    player_count = len(operator_players)
    if player_count == 0:
        log.info("There's no operator player.")
        return 0

    log.info(f"All {player_count} operator {pluralize("player", player_count)}:")
    print(sorted_players)
    return 0

def op_revoke(args: argparseNamespace) -> int:
    players: list[str] = args.players
    print(players)
    return 0

def search_projects(args: argparseNamespace) -> int:
    query: list[str] = args.query
    print(query)
    return 0

def show_projects(args: argparseNamespace) -> int:
    projects: list[str] = args.projects

    from .modrinth import api as modrinth_api
    from .shared import format_number

    project_information = modrinth_api.get_project_information(projects)
    for project in project_information:
        if "project_title" in project and "project_slug" in project:
            print(f"Name: {project['project_title']} ({project['project_slug']})")

        if "download_count" in project:
            print(f"Downloads: {format_number(project['download_count'])}")

        if "follower_count" in project:
            print(f"Followers: {format_number(project["follower_count"])}")

        if "project_slug" in project:
            print(f"Homepage: https://modrinth.com/{project['project_type']}/{project['project_slug']}")

    return 0

def start_server(args: argparseNamespace) -> int:
    import logging as log
    from . import state

    # Check MCServer status
    current_state = state.get_state()
    if current_state["is_active"]:
        log.error(f"There's another active MCServer process ({current_state["action"]}) running with process ID: {current_state["process_id"]}")
        return 1

    # Set state
    state.set_state("running_server")

    import os
    import shutil
    from pathlib import Path

    from . import config

    # Load configs
    launcher_config = config.load_config("launcher")

    jarfile = Path(launcher_config["jarfile"])
    memory_config = launcher_config["ram"]

    # Download jarfile
    if not jarfile.exists():
        import json
        from . import networking

        state.set_state("downloading_server")

        server_config = config.load_config("server")
        game_version = server_config["game_version"]
        server_loader = server_config["loader"]

        loader_name = server_loader["name"]
        loader_version = server_loader["version"]

        if loader_name != "vanilla" and loader_version is None:
            log.error(f"Loader version cannot be null")
            return 1

        match loader_name:
            # Mod loaders
            case "fabric":
                from .fabricmc import meta as fabricmc_meta

                log.info(f"Downloading Fabric loader {loader_version} for Minecraft version {game_version}...")
                networking.download(fabricmc_meta.download_url(game_version, loader_version, "1.0.1"), jarfile)
            
#            case "quilt":
#                log.info(f"Downloading Quilt loader {loader_version} for Minecraft version {game_version}...")
#                networking.download(f"https://")

#            case "legacy-fabric":
#                pass

            # Plugin loaders
            case "paper":
                from .papermc import api as papermc_api
                log.info(f"Downloading Paper build {loader_version} for Minecraft version {game_version}...")

                download_prop = papermc_api.get_project_build("paper", game_version, loader_version)["download_props"]["server:default"]
                networking.download(download_prop["download_url"], jarfile)
            case "purpur":
                from .purpurmc import api as purpurmc_api

                log.info(f"Downloading Purpur build {loader_version} for Minecraft version {game_version}...")
                networking.download(purpurmc_api.download_url("purpur", game_version, loader_version), jarfile)

            # Vanilla
            case "vanilla":
                from .mojang import manifest as mojang_manifest
                log.info(f"Downloading vanilla Minecraft version {game_version}...")

                version_manifest = mojang_manifest.get_version_manifest()["game_versions"]
                package_url = None
                for version in version_manifest:
                    if version["version_id"] == game_version:
                        package_url = version["package_url"]
                        break

                if package_url is None:
                    log.error(f"Minecraft version not found: {game_version}")
                    return 1

                package_data = networking.request(package_url)["text"]
                package_json = json.loads(package_data)
                version_download = package_json["downloads"]["server"]

                networking.download(version_download["url"], jarfile, hashes={
                    "sha1": version_download["sha1"]
                })
            case _:
                log.error(f"Loader is not supported: {loader_name}")

    # Check stuff
    if not shutil.which("java"):
        log.error("Java is not installed in PATH")
        return 1

    if memory_config["min"] > memory_config["max"]:
        log.error("Minimum RAM is bigger than maximum RAM")
        return 1

    # Run the server
    java_command_argv = [
        "java",
        f"-Xmx{memory_config['max']}M",
        f"-Xms{memory_config['min']}M",
        "-jar",
        str(jarfile)
    ]

    if launcher_config["is_nogui"]:
        java_command_argv.append("nogui")

    # Execute java
    log.debug(f"Executing command: {' '.join(java_command_argv)}")

    state.set_state("server_running")
    os.execvp(java_command_argv[0], java_command_argv)

def stop_server(args: argparseNamespace) -> int:
    force_stop: bool = args.force_stop

    import os
    import time
    import logging as log
    from signal import SIGKILL, SIGTERM

    from . import state

    current_state = state.get_state()
    if not current_state["is_active"]:
        log.error("Server is not running.")
        return 1

    log.info("Stopping server...")
    os.kill(current_state["process_id"], SIGTERM)

    current_state = state.get_state()
    if current_state["is_active"]:
        return 0

    if not force_stop:
        log.warning("Server appears to still be running, you may stop the server manually.")
        return 1

    from . import config
    launcher_config = config.load_config("launcher")
    time.sleep(launcher_config["force_stop"])

    log.warning("Server process still running, force stopping the server...")
    os.kill(current_state["process_id"], SIGKILL)
    return 1

# Whitelist
def whitelist_add(args: argparseNamespace) -> int:
    players: list[str] = args.players
    print(players)
    return 0

def whitelist_list(args: argparseNamespace) -> int:
    import logging as log
    from .server_files import whitelist
    from .shared import pluralize

    if not whitelist.whitelist_file.exists():
        log.error(f"File '{whitelist.whitelist_file}' not found.")
        return 1

    whitelisted_players = whitelist.list_players()

    player_list: list[str] = []
    for player in whitelisted_players:
        player_list.append(f"{player['player_name']} ({player['player_uuid']})")

    player_count: int = len(player_list)
    if player_count == 0:
        log.info("There are no whitelisted players.")
        return 0
    else:
        log.info(f"There {pluralize('is', player_count)} whitelisted {pluralize('player', player_count)}:")

    player_list.sort()
    print("\n".join(player_list))
    return 0

def whitelist_remove(args: argparseNamespace) -> int:
    players: list[str] = args.players
    print(players)
    return 0
