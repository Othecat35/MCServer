def main() -> int:
    import argparse
    import copy

    from . import __version__
    from .commands import add_projects
    from .commands import import_setup
    from .commands import init_server
    from .commands import list_projects
    from .commands import op_grant
    from .commands import op_list
    from .commands import op_revoke
    from .commands import search_projects
    from .commands import show_projects
    from .commands import start_server
    from .commands import stop_server
    from .commands import whitelist_add
    from .commands import whitelist_list
    from .commands import whitelist_remove

    from .shared import default_configs
    from .shared import loader_list

    def print_help(args: argparse.Namespace) -> int:
        parser: argparse.ArgumentParser = args.parser
        parser.print_help()
        return 0

    parser = argparse.ArgumentParser(
        prog="mcserver",
        description="A CLI tool for managing Minecraft: Java Edition servers.",
        epilog="Only created for Linux.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prefix_chars="-",
        add_help=True,
        allow_abbrev=False,
        exit_on_error=True,
        suggest_on_error=True,
        color=True)

    parser.set_defaults(func=print_help, parser=parser)
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + ".".join(map(str, __version__)))

    commands = parser.add_subparsers(title="Commands")

    # 'add' command
    add_command = commands.add_parser(
        "add",
        help="Add mods/projects",
        description="Add mods/plugins and their dependencies.")

    add_command.set_defaults(func=add_projects)
    add_command.add_argument(
        "projects",
        nargs="+",
        type=str,
        help="Project slugs or IDs")

    # 'import' command
    import_command = commands.add_parser(
        "import",
        help="Import a Modrinth modpack",
        description="Import a Modrinth modpack from a file.")

    import_command.set_defaults(func=import_setup)
    import_command.add_argument(
        "modpack",
        type=str,
        help="The Modrinth modpack file")

    # 'init' command
    init_command = commands.add_parser(
        "init",
        help="Initialize server configurations",
        description="Initialize the server configurations.")

    init_command.set_defaults(func=init_server)
    init_command.add_argument("--mc-version",
        default="latest-release",
        type=str,
        help="Minecraft version of the server",
        metavar="Version",
        dest="game_version")

    init_command.add_argument("--loader",
        default="vanilla",
        type=str,
        choices=loader_list,
        help="Loader for the server",
        metavar="Loader",
        dest="loader_name")

    init_command.add_argument("--loader-version",
        default="latest",
        type=str,
        help="Version of the loader",
        metavar="Version")

    init_command.add_argument(
        "--min-ram",
        default=512,
        type=int,
        help="Minimum RAM for the server (in MebiBytes)",
        metavar="Size")

    init_command.add_argument(
        "--max-ram",
        default=2048,
        type=int,
        help="Maximum RAM for the server (in MebiBytes)",
        metavar="Size")

    # 'list' command
    list_command = commands.add_parser(
        "list",
        help="List all added projects",
        description="List all added projects.")

    list_command.set_defaults(func=list_projects)

    # 'op' command
    op_command = commands.add_parser(
        "op",
        help="Manage operator players",
        description="Manage the operator status.")

    op_command.set_defaults(func=print_help, parser=op_command)
    op_subcommands = op_command.add_subparsers(title="Subcommands")

    # 'op grant'
    op_grant_command = op_subcommands.add_parser(
        "grant",
        help="Grant operator to players",
        description="Grant operator status to players.")

    op_grant_command.set_defaults(func=op_grant)
    op_grant_command.add_argument(
        "players",
        nargs="+",
        type=str,
        help="Player names or UUIDs")

    # 'op list'
    op_list_command = op_subcommands.add_parser(
        "list",
        help="List operator players",
        description="List all operator players.")

    op_list_command.set_defaults(func=op_list)

    # 'op revoke'
    op_revoke_command = op_subcommands.add_parser(
        "revoke",
        help="Revoke operator from players",
        description="Revoke operator status from players.")

    op_revoke_command.set_defaults(func=op_revoke)
    op_revoke_command.add_argument(
        "players",
        nargs="+",
        type=str,
        help="Player names or UUIDs")

    # 'search' command
    search_command = commands.add_parser(
        "search",
        help="Search Modrinth projects",
        description="Search projects from Modrinth.")

    search_command.set_defaults(func=search_projects)
    search_command.add_argument(
        "query",
        nargs="*",
        type=str,
        help="Query to search")

    # 'show' command
    show_command = commands.add_parser(
        "show",
        help="Show Modrinth project information",
        description="Show information about Modrinth projects.")

    show_command.set_defaults(func=show_projects)
    show_command.add_argument(
        "projects",
        nargs="+",
        type=str,
        help="Project slugs or IDs")

    # 'start' command
    start_command = commands.add_parser(
        "start",
        help="Start the server",
        description="Install and start the server.")

    start_command.set_defaults(func=start_server)

    # "stop" command
    stop_command = commands.add_parser(
        "stop",
        help="Stop the server",
        description="Stop the running server")

    stop_command.set_defaults(func=stop_server)
    stop_command.add_argument(
        "--force-stop",
        action="store_true",
        type=bool,
        help="Force stop the server")

     # 'whitelist' command
    whitelist_command = commands.add_parser(
        "whitelist",
        help="Manage whitelisted players",
        description="Manage the whitelisted players.")

    whitelist_command.set_defaults(func=print_help, parser=whitelist_command)
    whitelist_subcommands = whitelist_command.add_subparsers(title="Subcommands")

    # 'whitelist add'
    whitelist_add_command = whitelist_subcommands.add_parser(
        "add",
        help="Add players to whitelist",
        description="Add players to the whitelist.")

    whitelist_add_command.set_defaults(func=whitelist_add)
    whitelist_add_command.add_argument(
        "players",
        nargs="+",
        type=str,
        help="Player names or UUIDs")

    # 'whitelist list'
    whitelist_list_command = whitelist_subcommands.add_parser(
        "list",
        help="List whitelisted players",
        description="List all whitelisted playeers.")

    whitelist_list_command.set_defaults(func=whitelist_list)

    # 'whitelist remove'
    whitelist_remove_command = whitelist_subcommands.add_parser(
        "remove",
        help="Remove players from whitelist",
        description="Remove players from the whitelist.")

    whitelist_remove_command.set_defaults(func=whitelist_remove)
    whitelist_remove_command.add_argument(
        "players",
        nargs="+",
        type=str,
        help="Player names or UUIDs")

    args = parser.parse_args()
    return args.func(args)
