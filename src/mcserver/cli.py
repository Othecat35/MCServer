def main() -> int:
    import argparse

    from . import __version__
    from .modrinth.shared import search_sort_index
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
                import logging as log

                log.error(f"Unknown command: {command_name}")
                return 1

    # Parser Setup
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
        help="Add Modrinth projects to the server",
        description="Add Modrinth mods/plugins to the server",
    )

    add_command.set_defaults(command_name="add")
    add_command.add_argument(
        "projects", nargs="+", type=str, help="Modrinth project slugs or IDs"
    )

    # 'import' command
    import_command = commands.add_parser(
        "import",
        help="Import a Modrinth modpack",
        description="Import a Modrinth modpack from a file.",
    )

    import_command.set_defaults(command_name="import")
    import_command.add_argument("file", type=str, help="The Modrinth modpack file")

    # 'init' command
    init_command = commands.add_parser(
        "init",
        help="Initialize server configurations",
        description="Initialize the server configurations.",
    )

    init_command.set_defaults(command_name="init")
    init_command.add_argument(
        "--game-version",
        default="latest-release",
        type=str,
        help="Minecraft version of the server",
        metavar="Version",
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

    init_command.add_argument(
        "--search-limit",
        default=20,
        type=int,
        help="Default search limit value",
        metavar="Number",
        dest="search_limit",
    )

    init_command.add_argument(
        "--search-sort",
        default="relevance",
        type=str,
        choices=search_sort_index,
        help="Default search sort index",
        metavar="Index",
        dest="search_limit",
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

    # op_grant and op_revoke is not going to be implemented in this version
    # 'op list'
    op_list_command = op_subcommands.add_parser(
        "list", help="List operator players", description="List all operator players."
    )

    op_list_command.set_defaults(command_name="op_list")

    # 'remove' command
    remove_command = commands.add_parser(
        "remove", help="Remove projects", description="Remove projects"
    )

    remove_command.set_defaults(command_name="remove")
    remove_command.add_argument(
        "projects", nargs="+", type=str, help="Modrinth project slugs or IDs"
    )

    # 'search' command
    search_command = commands.add_parser(
        "search",
        help="Search Modrinth projects",
        description="Search projects from Modrinth.",
    )

    search_command.set_defaults(command_name="search")
    search_command.add_argument(
        "search_query", nargs="*", type=str, help="Query to search"
    )

    search_command.add_argument(
        "--limit",
        default=20,
        type=int,
        help="Search projects per page",
        metavar="Number",
        dest="search_limit",
    )

    search_command.add_argument(
        "--page",
        default=1,
        type=int,
        help="Show mods in page number",
        metavar="Number",
        dest="page_number",
    )

    search_command.add_argument(
        "--sort",
        default="relevance",
        type=str,
        choices=search_sort_index,
        help="Sort by index",
        metavar="Index",
        dest="sort_index",
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
        help="Ignore game version at all",
    )

    search_command.add_argument(
        "--loader",
        type=str,
        choices=loader_list,
        help="Override the loader filter",
        metavar="Loader",
        dest="loader_name",
    )

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

    # status_command is not going to be implemented in this version
    # "stop" command
    stop_command = commands.add_parser(
        "stop", help="Stop the server", description="Stop the running server"
    )

    stop_command.set_defaults(command_name="stop")

    # "update" command
    update_command = commands.add_parser(
        "update",
        help="Update projects from Modrinth",
        description="Update projects from Modrinth",
    )

    update_command.set_defaults(command_name="update")

    # 'whitelist' command
    whitelist_command = commands.add_parser(
        "whitelist",
        help="Manage whitelisted players",
        description="Manage the player whitelist.",
    )

    whitelist_command.set_defaults(parser=whitelist_command)
    whitelist_subcommands = whitelist_command.add_subparsers(title="Subcommands")

    # whitelist_add and whitelist_remove is not going to be implemented in this version
    # 'whitelist list'
    whitelist_list_command = whitelist_subcommands.add_parser(
        "list",
        help="List whitelisted players",
        description="List all whitelisted players.",
    )

    whitelist_list_command.set_defaults(command_name="whitelist_list")

    args = parser.parse_args()
    return args.func(args)
