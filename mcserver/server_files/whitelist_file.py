# #Modules
# import json
# from pathlib import Path
# from typing import TypedDict
# from uuid import UUID

# #Paths
# whitelist_file = Path("whitelist.json")

# #TypedDicts
# class WHitelistedPlayerIdentity(TypedDict):
#     player_uuid: UUID
#     player_name: str

# #Functions
# def add_player(player_uuid: UUID | str, player_name: str) -> None:
#     if isinstance(player_uuid, str):
#         player_uuid = UUID(player_uuid)

#     with open(whitelist_file, mode="r+") as file:
#         whitelist_data = json.load(file)
#         whitelist_data.append({
#             "uuid": str(player_uuid),
#             "name": player_name
#         })

#         file.seek(0)
#         json.dump(whitelist_data, file, indent=2)
#         file.truncate()

# # TODO: Complete this function
# # def list_players() -> list[WhitelistedPlayerIdentity]:
# #     pass

# def remove_player(player_uuid: UUID | str | None = None, player_name: str | None = None) -> None:
#     if player_uuid is None and player_name is None:
#         raise ValueError("At least one of 'player_uuid' or 'player_name' must be provided.")

#     if isinstance(player_uuid, str):
#         player_uuid = UUID(player_uuid)

#     with open(whitelist_file, mode="r+") as file:
#         whitelist_data = json.load(file)

#         new_data = []
#         for player_identity in whitelist_data:
#             if :
#                 continue
#             elif player_identity["name"] == player_name:
#                 continue

#             new_data.append(player_identity)

#         file.seek(0)
#         json.dump(new_data, file, indent=2)
#         file.truncate()
