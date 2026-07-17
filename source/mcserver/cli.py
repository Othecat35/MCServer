def main() -> int:
    import argparse

    def print_help(args: argparse.Namespace) -> int:
        parser: argparse.ArgumentParser = args.parser
        parser.print_help()
        return 0

    parser = argparse.ArgumentParser(
        prog="mcserver",
        description="A CLI tool for managing Minecraft: Java Edition servers.",
        epilog="Not created for Windows",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prefix_chars="-",
        add_help=True,
        allow_abbrev=False,
        exit_on_error=True,
        suggest_on_error=True,
        color=True)

    parser.set_defaults(func=print_help, parser=parser)

    from . import __version__
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + ".".join(map(str, __version__)))

    commands = parser.add_subparsers(title="Commands")

    # 'add' command
    add_command = commands.add_parser(
        "add",
        help="Add Modrinth projects",
        description="Add Modrinth projects")
    
    from .commands import add_projects
    add_command.set_defaults(func=add_projects)

    add_command.add_argument(
        "projects",
        nargs="+",
        type=str,
        help="Project slugs or IDs")

    # 'import' command
    import_command = commands.add_parser(
        "import",
        help="Import Modrinth modpack",
        description="Import Modrinth modpack")

    from .commands import import_setup
    import_command.set_defaults(func=import_setup)

    # 'init' command
    init_command = commands.add_parser(
        "init",
        help="Initialize server configurations",
        description="Initialize server configurations")

    from .commands import init_server
    init_command.set_defaults(func=init_server)

    # 'list' command
    list_command = commands.add_parser(
        "list",
        help="List all downloaded projects",
        description="List all downloaded projects")

    from .commands import list_projects
    list_command.set_defaults(func=list_projects)

    # 'op' command
    op_command = commands.add_parser(
        "op",
        help="Manage operator players",
        description="Manage operator players")

    op_command.set_defaults(func=print_help, parser=op_command)
    op_subcommands = op_command.add_subparsers(title="Subcommands")

    # 'op grant'
    op_grant_command = op_subcommands.add_parser(
        "grant",
        help="Grant players operator",
        description="Grant players operator")
    
    from .commands import op_grant
    op_grant_command.set_defaults(func=op_grant)

    op_grant_command.add_argument(
        "players",
        nargs="+",
        type=str,
        help="Player names or UUIDs")

    # 'op list'
    op_list_command = op_subcommands.add_parser(
        "list",
        help="List all operator players",
        description="List all operator players")

    from .commands import op_list
    op_list_command.set_defaults(func=op_list)

    # 'op revoke'
    op_revoke_command = op_subcommands.add_parser(
        "revoke",
        help="Revoke operator players",
        description="Remove operator players")

    from .commands import op_revoke
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
        description="Search Modrinth projects")
    
    from .commands import search_projects
    search_command.set_defaults(func=search_projects)

    search_command.add_argument(
        "query",
        nargs="*",
        type=str,
        help="Query to search")

    # 'show' command
    show_command = commands.add_parser(
        "show",
        help="Show Modrinth projects information",
        description="Show Modrinth projects information")

    from .commands import show_projects
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
        description="Start the server")

    from .commands import start_server
    start_command.set_defaults(func=start_server)

     # 'whitelist' command
    whitelist_command = commands.add_parser(
        "whitelist",
        help="Manage whitelisted players",
        description="Manage whitelisted players")

    whitelist_command.set_defaults(func=print_help, parser=whitelist_command)
    whitelist_subcommands = whitelist_command.add_subparsers(title="Subcommands")

    # 'whitelist add'
    whitelist_add_command = whitelist_subcommands.add_parser(
        "add",
        help="Add players to the whitelist",
        description="Add players to the whitelist")
    
    from .commands import whitelist_add
    whitelist_add_command.set_defaults(func=whitelist_add)

    whitelist_add_command.add_argument(
        "players",
        nargs="+",
        type=str,
        help="Player names or UUIDs")

    # 'whitelist list'
    whitelist_list_command = whitelist_subcommands.add_parser(
        "list",
        help="List all whitelisted players",
        description="List all whitelisted players")

    from .commands import whitelist_list
    whitelist_list_command.set_defaults(func=whitelist_list)

    # 'whitelist remove'
    whitelist_remove_command = whitelist_subcommands.add_parser(
        "remove",
        help="Remove players to the whitelist",
        description="Remove players from the whitelist")

    from .commands import whitelist_remove
    whitelist_remove_command.set_defaults(func=whitelist_remove)

    whitelist_remove_command.add_argument(
        "players",
        nargs="+",
        type=str,
        help="Player names or UUIDs")

    args = parser.parse_args()
    return args.func(args)
