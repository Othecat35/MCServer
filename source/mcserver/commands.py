#Modules
# Standard
import logging as log

from argparse import Namespace as argparseNamespace

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
    print(projects)
    return 0

def start_server(args: argparseNamespace) -> int:
    return 0

# Whitelist
def whitelist_add(args: argparseNamespace) -> int:
    players: list[str] = args.players
    print(players)
    return 0

def whitelist_list(args: argparseNamespace) -> int:
    from .server_files import whitelist

    if not whitelist.whitelist_file.exists():
        log.error("No 'whitelist.json' file found")
        return 1

    whitelisted_players = whitelist.list_players()

    player_ids: list[str] = []
    for player in whitelisted_players:
        player_ids.append(f"{player['player_name']} ({player['player_uuid']})")

    player_ids.sort()
    sorted_player_ids = "\n".join(player_ids)

    player_count = len(whitelisted_players)
    log.info(f"All {player_count} whitelisted {pluralize("player", player_count)}:")
    print(sorted_player_ids)
    return 0

def whitelist_remove(args: argparseNamespace) -> int:
    players: list[str] = args.players
    print(players)
    return 0
