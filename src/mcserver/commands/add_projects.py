from argparse import Namespace as argparseNamespace


def main(args: argparseNamespace) -> int:
    projects: list[str] = args.projects
    print(args)
    return 0
