from argparse import Namespace as argparseNamespace
def main(args: argparseNamespace) -> int:
    players: list[str] = args.players
    print(args)
    return 0
