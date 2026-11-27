import argparse
import sys
from collections.abc import Callable
from pathlib import Path

from . import __version__
from .modrinth.shared import search_sort_index
from .shared import loader_list


def bound_int(min_integer: int, max_integer: int | None = None) -> Callable:
    def parse(cli_string: str) -> int:
        try:
            integer: int = int(cli_string)
        except ValueError:
            raise argparse.ArgumentTypeError(f"{cli_string} is not an integer")

        if integer < min_integer:
            raise argparse.ArgumentTypeError(
                f"{integer} must be higher than or equal to {min_integer}"
            )

        if max_integer is not None and integer > max_integer:
            raise argparse.ArgumentTypeError(
                f"{integer} must be between {min_integer} and {max_integer}"
            )

        return integer

    return parse


def command_function(args: argparse.Namespace) -> int:
    command_name: str = args.command_name

    match command_name:
        case "add":
            from .commands import add_projects

            return add_projects(args)
        case "import":
            from .commands import import_setup

            return import_setup(args)
        case "help":
            from .commands import print_help

            return print_help(args)
        case "init":
            from .commands import initialize_server

            return initialize_server(args)
        case "list":
            from .commands import list_projects

            return list_projects(args)
        case "op_grant":
            from .commands import op_grant

            return op_grant(args)
        case "op_list":
            from .commands import op_list

            return op_list(args)
        case "op_revoke":
            from .commands import op_revoke

            return op_revoke(args)
        case "remove":
            from .commands import remove_projects

            return remove_projects(args)
        case "search":
            from .commands import search_projects

            return search_projects(args)
        case "show":
            from .commands import show_projects

            return show_projects(args)
        case "start":
            from .commands import start_server

            return start_server(args)
        case "status":
            from .commands import server_status

            return server_status(args)
        case "stop":
            from .commands import stop_server

            return stop_server(args)
        case "update":
            from .commands import update_projects

            return update_projects(args)
        case "whitelist_add":
            from .commands import whitelist_add

            return whitelist_add(args)
        case "whitelist_list":
            from .commands import whitelist_list

            return whitelist_list(args)
        case "whitelist_remove":
            from .commands import whitelist_remove

            return whitelist_remove(args)
        case _:
            import logging

            logger = logging.getLogger(__name__)

            logger.error(f"Unknown command: {command_name}")
            return 1


# Reusable flags
directory_parser: argparse.ArgumentParser = argparse.ArgumentParser(add_help=False)
current_dir: Path = Path.cwd()
directory_parser.add_argument(
    "--directory",
    default=current_dir,
    type=Path,
    help="Working directory for the command",
    metavar="Path",
)

player_parser: argparse.ArgumentParser = argparse.ArgumentParser(add_help=False)
player_parser.add_argument(
    "players",
    nargs="+",
    type=str,
    help="List of player names or UUIDs",
    metavar="Players",
)

# Parser Setup
parser: argparse.ArgumentParser = argparse.ArgumentParser(
    description="A CLI tool for managing Minecraft: Java Edition servers.",
    epilog="Designed for Linux and Termux.",
    parents=[directory_parser],
    add_help=True,
    allow_abbrev=False,
)

if sys.version_info >= (3, 14):
    parser.suggest_on_error = True
    parser.color = True

parser.set_defaults(func=command_function, command_name="help", parser=parser)
parser.add_argument(
    "-v",
    "--version",
    action="version",
    version="%(prog)s " + __version__,
)

commands: argparse.Action = parser.add_subparsers(title="Commands")

# 'add' command
add_command: argparse.ArgumentParser = commands.add_parser(
    "add", help="Add mods or plugins", description="Add mods or plugins to the server."
)

add_command.set_defaults(command_name="add")
add_command.add_argument("projects", nargs="+", type=str, help="Project names")

# 'init' command
init_command: argparse.ArgumentParser = commands.add_parser(
    "init",
    help="Initialize server configuration",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Initialize a new server configuration.",
)

init_command.set_defaults(command_name="init")

init_command.add_argument(
    "--game-version",
    default="latest-release",
    type=str,
    help="Minecraft version to use",
    metavar="Version",
)

init_command.add_argument(
    "--loader",
    default="vanilla",
    type=str,
    choices=loader_list,
    help="Mod loader to use",
    metavar="Loader",
    dest="loader_name",
)

init_command.add_argument(
    "--loader-version",
    default="latest",
    type=str,
    help="Version of the mod loader to use",
    metavar="Version",
)

init_command.add_argument(
    "--min-ram",
    default=512,
    type=bound_int(512),
    help="Minimum memory allocation in MiB",
    metavar="512+ MiB",
)

init_command.add_argument(
    "--max-ram",
    default=1024,
    type=bound_int(1024),
    help="Maximum memory allocation in MiB",
    metavar="1024+ MiB",
)

init_command.add_argument(
    "--search-limit",
    default=20,
    type=bound_int(1, 100),
    help="Number of projects to retrieve per search",
    metavar="1-100",
    dest="search_limit",
)

init_command.add_argument(
    "--search-sort",
    default="relevance",
    type=str,
    choices=search_sort_index,
    help="Sort order for search results",
    metavar="Index",
    dest="sort_index",
)

# 'list' command
list_command: argparse.ArgumentParser = commands.add_parser(
    "list",
    help="List added projects",
    description="List add mods/plugins",
)

list_command.set_defaults(command_name="list")

# 'op' command
op_command: argparse.ArgumentParser = commands.add_parser(
    "op",
    help="Manage operator permissions",
    description="Manage player operator permissions.",
)

op_command.set_defaults(parser=op_command)
op_subcommands: argparse.Action = op_command.add_subparsers(title="Subcommands")

# 'op grant'
op_grant_command: argparse.ArgumentParser = op_subcommands.add_parser(
    "grant",
    help="Grant operator permissions to players",
    parents=[player_parser],
    description="Grant operator permissions to one or more players.",
)

op_grant_command.set_defaults(command_name="op_grant")

op_grant_command.add_argument(
    "--bypasses-player-limit",
    action="store_true",
    help="Allow players to bypass the server player limit",
)

op_grant_command.add_argument(
    "--online-mode",
    type=str,
    choices=["true", "false"],
    metavar="{true,false}",
    help="Override the server's online-mode setting",
)

op_grant_command.add_argument(
    "--permission-level",
    type=bound_int(0, 4),
    metavar="0-4",
    help="Operator permission level",
)

# 'op list'
op_list_command: argparse.ArgumentParser = op_subcommands.add_parser(
    "list",
    help="List operator players",
    description="Display all players with operator permissions.",
)

op_list_command.set_defaults(command_name="op_list")

# 'op revoke'
op_revoke_command: argparse.ArgumentParser = op_subcommands.add_parser(
    "revoke",
    help="Revoke operator permissions from players",
    parents=[player_parser],
    description="Revoke operator permissions from one or more players.",
)

op_revoke_command.set_defaults(command_name="op_revoke")

# 'search' command
search_command: argparse.ArgumentParser = commands.add_parser(
    "search",
    help="Search Modrinth projects",
    description="Search for projects on Modrinth.",
)

search_command.set_defaults(command_name="search")

search_command.add_argument(
    "search_query",
    nargs="*",
    type=str,
    help="Search terms to use",
)

search_command.add_argument(
    "--limit",
    type=bound_int(1, 100),
    help="Number of projects to retrieve per page",
    metavar="1-100",
    dest="search_limit",
)

search_command.add_argument(
    "--page",
    default=1,
    type=bound_int(1),
    help="Page number to retrieve",
    metavar="1+",
    dest="page_number",
)

search_command.add_argument(
    "--sort-index",
    type=str,
    choices=search_sort_index,
    help="Sort order for search results",
    metavar="Index",
)

search_command.add_argument(
    "--game-version",
    type=str,
    help="Override the Minecraft version filter",
    metavar="Version",
    dest="game_version",
)

search_command.add_argument(
    "--no-version",
    action="store_true",
    help="Disable the Minecraft version filter",
)

search_command.add_argument(
    "--loader",
    type=str,
    choices=loader_list,
    help="Override the mod loader filter",
    metavar="Loader",
    dest="loader_name",
)

# 'show' command
show_command: argparse.ArgumentParser = commands.add_parser(
    "show",
    help="Show Modrinth project information",
    description="Show information about Modrinth projects",
)

show_command.set_defaults(command_name="show")
show_command.add_argument("projects", nargs="+", type=str, help="Project slugs or IDs")

# 'start' command
start_command: argparse.ArgumentParser = commands.add_parser(
    "start", help="Start the server", description="Install and start the server"
)

start_command.set_defaults(command_name="start")

# status_command is not going to be implemented in this version
# "stop" command
stop_command: argparse.ArgumentParser = commands.add_parser(
    "stop", help="Stop the server", description="Stop the running server"
)

stop_command.set_defaults(command_name="stop")

# update is not going to be implemented in this version
# 'whitelist' command

whitelist_command: argparse.ArgumentParser = commands.add_parser(
    "whitelist",
    help="Manage the player whitelist",
    description="Manage the server's player whitelist.",
)

whitelist_command.set_defaults(parser=whitelist_command)
whitelist_subcommands: argparse.Action = whitelist_command.add_subparsers(
    title="Subcommands",
)

# 'whitelist add'
whitelist_add_command: argparse.ArgumentParser = whitelist_subcommands.add_parser(
    "add",
    help="Add players to the whitelist",
    parents=[player_parser],
    description="Add one or more players to the server whitelist.",
)

whitelist_add_command.set_defaults(command_name="whitelist_add")

whitelist_add_command.add_argument(
    "--online-mode",
    type=str,
    choices=["true", "false"],
    metavar="{true,false}",
    help="Override the server's online-mode setting",
)

# 'whitelist list'
whitelist_list_command: argparse.ArgumentParser = whitelist_subcommands.add_parser(
    "list",
    help="List whitelisted players",
    description="Display all players currently on the server whitelist.",
)

whitelist_list_command.set_defaults(command_name="whitelist_list")

# 'whitelist remove'
whitelist_remove_command: argparse.ArgumentParser = whitelist_subcommands.add_parser(
    "remove",
    help="Remove players from the whitelist",
    parents=[player_parser],
    description="Remove one or more players from the server whitelist.",
)

whitelist_remove_command.set_defaults(command_name="whitelist_remove")


def main() -> int:
    args: argparse.Namespace = parser.parse_args()
    return args.func(args)
