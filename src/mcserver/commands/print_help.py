import argparse


def run(args: argparse.Namespace) -> int:
    parser: argparse.ArgumentParser = args.parser
    parser.print_help()
    return 1
