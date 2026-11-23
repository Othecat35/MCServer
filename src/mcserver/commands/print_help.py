import argparse


def print_help(args: argparse.Namespace) -> int:
    parser: argparse.ArgumentParser = args.parser
    parser.print_help()
    return 1
