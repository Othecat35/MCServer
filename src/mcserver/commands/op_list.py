from argparse import Namespace as argparseNamespace
def main(args: argparseNamespace) -> int:
    import logging as log
    from ..server_files import ops
    from ..shared import pluralize

    if not ops.ops_file.exists():
        log.error(f"File '{ops.ops_file}' not found.")
        return 1

    operator_players = ops.list_players()

    players: list[str] = []
    for player in operator_players:
        players.append(f"{player['player_name']} ({player['player_uuid']}) Level: {player["permission_level"]}")

    players.sort()
    sorted_players = "\n".join(players)

    player_count = len(operator_players)
    if player_count == 0:
        log.info("There's no operator player.")
        return 0

    log.info(f"All {player_count} operator {pluralize("player", player_count)}:")
    print(sorted_players)
    return 0
