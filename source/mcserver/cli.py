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
        fromfile_prefix_chars="@",
        add_help=True,
        allow_abbrev=False,
        exit_on_error=True,
        suggest_on_error=True,
        color=True)

    parser.set_defaults(func=print_help, parser=parser)
    parser.add_argument("--version", action="version")

    args = parser.parse_args()
    return args.func(args)
