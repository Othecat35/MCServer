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
