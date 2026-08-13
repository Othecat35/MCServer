import argparse


def main(args: argparse.Namespace) -> int:
    import logging as log

    from ..server_files import whitelist
    from ..shared import pluralize

    if not whitelist.whitelist_file.exists():
        log.error(f"File '{whitelist.whitelist_file}' not found.")
        return 1

    whitelisted_players = whitelist.list_players()

    player_list: list[str] = []
    for player in whitelisted_players:
        player_list.append(f"{player['player_name']} ({player['player_uuid']})")

    player_count: int = len(player_list)
    if player_count == 0:
        log.info("There are no whitelisted players.")
        return 0
    else:
        log.info(
            f"There {pluralize('is', player_count)} whitelisted {pluralize('player', player_count)}:"
        )

    player_list.sort()
    print("\n".join(player_list))
    return 0
