from argparse import Namespace as argparseNamespace
def main(args: argparseNamespace) -> int:
    query: list[str] = args.query
    print(args)
    return 0
