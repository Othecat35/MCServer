def main() -> int:
    import argparse

    from . import __version__
    from .shared import loader_list

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
            case "search":
                from .commands import search_projects

                return search_projects(args)
            case "show":
                from .commands import show_projects

                return show_projects(args)
            case "start":
                from .commands import start_server

                return start_server(args)
            case "stop":
                from .commands import stop_server

                return stop_server(args)
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
                import logging as log

                log.error(f"Unknown command: {command_name}")
                return 1

    parser = argparse.ArgumentParser(
        prog="mcserver",
        description="A CLI tool for managing Minecraft: Java Edition servers.",
        epilog="Created for Linux and Termux only.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prefix_chars="-",
        add_help=True,
        allow_abbrev=False,
        exit_on_error=True,
        suggest_on_error=True,
        color=True,
    )

    parser.set_defaults(func=command_function, command_name="help", parser=parser)
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )

    commands = parser.add_subparsers(title="Commands")

    # 'add' command
    add_command = commands.add_parser(
        "add",
        help="Add mods/projects",
        description="Add mods/plugins and their dependencies.",
    )

    add_command.set_defaults(command_name="add")
    add_command.add_argument(
        "projects", nargs="+", type=str, help="Project slugs or IDs"
    )

    # 'import' command
    import_command = commands.add_parser(
        "import",
        help="Import a Modrinth modpack",
        description="Import a Modrinth modpack from a file.",
    )

    import_command.set_defaults(command_name="import")
    import_command.add_argument("modpack", type=str, help="The Modrinth modpack file")

    # 'init' command
    init_command = commands.add_parser(
        "init",
        help="Initialize server configurations",
        description="Initialize the server configurations.",
    )

    init_command.set_defaults(command_name="init")
    init_command.add_argument(
        "--mc-version",
        default="latest-release",
        type=str,
        help="Minecraft version of the server",
        metavar="Version",
        dest="game_version",
    )

    init_command.add_argument(
        "--loader",
        default="vanilla",
        type=str,
        choices=loader_list,
        help="Loader for the server",
        metavar="Loader",
        dest="loader_name",
    )

    init_command.add_argument(
        "--loader-version",
        default="latest",
        type=str,
        help="Version of the loader",
        metavar="Version",
    )

    init_command.add_argument(
        "--min-ram",
        default=512,
        type=int,
        help="Minimum RAM for the server (in MebiBytes)",
        metavar="Size",
    )

    init_command.add_argument(
        "--max-ram",
        default=2048,
        type=int,
        help="Maximum RAM for the server (in MebiBytes)",
        metavar="Size",
    )

    # 'list' command
    list_command = commands.add_parser(
        "list", help="List all added projects", description="List all added projects."
    )

    list_command.set_defaults(command_name="list")

    # 'op' command
    op_command = commands.add_parser(
        "op", help="Manage operator players", description="Manage the operator status."
    )

    op_command.set_defaults(parser=op_command)
    op_subcommands = op_command.add_subparsers(title="Subcommands")

    # 'op grant'
    op_grant_command = op_subcommands.add_parser(
        "grant",
        help="Grant operator to players",
        description="Grant operator status to players.",
    )

    op_grant_command.set_defaults(command_name="op_grant")
    op_grant_command.add_argument(
        "players", nargs="+", type=str, help="Player names or UUIDs"
    )

    # 'op list'
    op_list_command = op_subcommands.add_parser(
        "list", help="List operator players", description="List all operator players."
    )

    op_list_command.set_defaults(command_name="op_list")

    # 'op revoke'
    op_revoke_command = op_subcommands.add_parser(
        "revoke",
        help="Revoke operator from players",
        description="Revoke operator status from players.",
    )

    op_revoke_command.set_defaults(command_name="op_revoke")
    op_revoke_command.add_argument(
        "players", nargs="+", type=str, help="Player names or UUIDs"
    )

    # 'remove' command
    remove_command = commands.add_parser(
        "remove",
        help="Remove projects",
        description="Remove projects"
    )

    

    # 'search' command
    search_command = commands.add_parser(
        "search",
        help="Search Modrinth projects",
        description="Search projects from Modrinth.",
    )

    search_command.set_defaults(command_name="search")
    search_command.add_argument("query", nargs="*", type=str, help="Query to search")

    # 'show' command
    show_command = commands.add_parser(
        "show",
        help="Show Modrinth project information",
        description="Show information about Modrinth projects.",
    )

    show_command.set_defaults(command_name="show")
    show_command.add_argument(
        "projects", nargs="+", type=str, help="Project slugs or IDs"
    )

    # 'start' command
    start_command = commands.add_parser(
        "start", help="Start the server", description="Install and start the server."
    )

    start_command.set_defaults(command_name="start")

    # "stop" command
    stop_command = commands.add_parser(
        "stop", help="Stop the server", description="Stop the running server"
    )

    stop_command.set_defaults(command_name="stop")
    stop_command.add_argument(
        "--force-stop", action="store_true", help="Force stop the server"
    )

    # "update" command
    update_command = commands.add_parser(
        "update",
        help="Update projects from Modrinth",
        description="Update projects from Modrinth"
    )

    # 'whitelist' command
    whitelist_command = commands.add_parser(
        "whitelist",
        help="Manage whitelisted players",
        description="Manage the player whitelist.",
    )

    whitelist_command.set_defaults(parser=whitelist_command)
    whitelist_subcommands = whitelist_command.add_subparsers(title="Subcommands")

    # 'whitelist add'
    whitelist_add_command = whitelist_subcommands.add_parser(
        "add",
        help="Add players to whitelist",
        description="Add players to the whitelist.",
    )

    whitelist_add_command.set_defaults(command_name="whitelist_add")
    whitelist_add_command.add_argument(
        "players", nargs="+", type=str, help="Player names or UUIDs"
    )

    # 'whitelist list'
    whitelist_list_command = whitelist_subcommands.add_parser(
        "list",
        help="List whitelisted players",
        description="List all whitelisted players.",
    )

    whitelist_list_command.set_defaults(command_name="whitelist_list")

    # 'whitelist remove'
    whitelist_remove_command = whitelist_subcommands.add_parser(
        "remove",
        help="Remove players from whitelist",
        description="Remove players from the whitelist.",
    )

    whitelist_remove_command.set_defaults(command_name="whitelist_remove")
    whitelist_remove_command.add_argument(
        "players", nargs="+", type=str, help="Player names or UUIDs"
    )

    args = parser.parse_args()
    return args.func(args)
