from argparse import Namespace


def main(args: Namespace) -> int:
    players: list[str] = args.players
    import logging as log

    # from uuid import UUID
    # from ..server_files.whitelist import remove_players
    # from ..minecraft.player_identity import PlayerID

    log.error("Command is not implemented yet.")
    # player_ids: list[PlayerID] = []
    # for player in players:
    #     try:
    #         UUID(player)
    #         log.debug(f"{player} is likely an UUID")
    #         player_id: PlayerID = {"player_uuid": player}

    #         player_ids.append(player_id)
    #     except ValueError:
    #         log.debug(f"{player} is likely a name")
    #         player_id: PlayerID = {"player_name": player}

    #         player_ids.append(player_id)

    # try:
    #     remove_players(player_ids)
    # except FileNotFoundError as error:
    #     log.error(error)
    #     return 1

    return 1
