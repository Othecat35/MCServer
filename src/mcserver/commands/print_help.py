import argparse
def main(args: argparse.Namespace) -> int:
    parser: argparse.ArgumentParser = args.parser
    parser.print_help()
    return 0
