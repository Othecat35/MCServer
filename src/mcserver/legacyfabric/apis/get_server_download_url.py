from ...urls import legacyfabric_meta_url


def get_server_download_url(game_version: str, loader_version: str, installer_version: str) -> str:
    return f"{legacyfabric_meta_url}/v2/versions/loader/{game_version}/{loader_version}/{installer_version}/server/jar"
