#Modules
# Standard
import logging as log

from argparse import Namespace as argparseNamespace
from pathlib import Path
from uuid import UUID

# MCServer
from .shared import pluralize

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

    from . import config
    from .shared import default_configs
    from .shared import mcserver_dir
    from .shared import merge_dict

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

    # Creating the directories
    mcserver_dir.mkdir(exist_ok=True)
    config.configs_dir.mkdir(exist_ok=True)

    for config_name in default_configs.keys():
        default_config = copy.deepcopy(default_configs[config_name])

        config_override = {}
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

        config_data = merge_dict(default_config, config_override)
        config.generate_config(config_name, config_data)

    print(game_version, loader_name, loader_version, min_ram, max_ram)
    return 0

def list_projects(args: argparseNamespace) -> int:
    return 0

# Operators
def op_grant(args: argparseNamespace) -> int:
    players: list[str] = args.players
    print(players)
    return 0

def op_list(args: argparseNamespace) -> int:
    from .server_files import ops

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

    project_information = modrinth_api.get_project_information(projects)
    for project in project_information:
        print(project)

    return 0

def start_server(args: argparseNamespace) -> int:
    from . import state
    
    if state.is_active():
        current_state = state.get_state()
        log.error(f"There's another active MCServer process ({current_state["action"]}) running with process ID: {current_state["process_id"]}")
        return 1

    return 0

def stop_server(args: argparseNamespace) -> int:
    force_stop: bool = args.force_stop

    import os
    import time

    from signal import SIGKILL, SIGTERM

    from . import state

    if not state.is_active():
        log.error("Server is not running.")
        return 1

    current_state = state.get_state()

    log.info("Stopping server...")
    os.kill(current_state["process_id"], SIGTERM)

    time.sleep(15)

    if state.is_active():
        return 0

    if not force_stop:
        log.warning("Server appears to still be running, you may stop the server manually.")
        return 1

    current_state = state.get_state()

    log.warning("Server process still running, force stopping the server...")
    os.kill(current_state["process_id"], SIGKILL)

    return 1

# Whitelist
def whitelist_add(args: argparseNamespace) -> int:
    players: list[str] = args.players
    print(players)
    return 0

def whitelist_list(args: argparseNamespace) -> int:
    from .server_files import whitelist

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
