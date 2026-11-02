import argparse

from ..server_files import whitelist


def run(args: argparse.Namespace) -> int:
    player_identifiers: list[str] = args.players

    player_names: list[str] = []
    player_uuids: list[str] = []
    for player in player_identifiers:
        if len(player) > 16:
            print(f"{player} probably an UUID (I think)")
            player_uuids.append(player)
        else:
            print(f"{player} is probably just a name (I think)")
            player_names.append(player)

    print("Oh hi there!")
    print(f"So I'm guessing that '{', '.join(player_names)}' is/are usernames and '{', '.join(player_uuids)}' are UUIDs?")
    return 0