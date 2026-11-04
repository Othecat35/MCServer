import logging

from . import properties
from .paths import server_properties_file_path

logger = logging.getLogger(__name__)

def get_online_mode() -> bool:
    """Get the online mode of the server
    If the file does not exists, its True. If it does exist but it doesn't have the online-mode, its
    True. If it does have online-mode, but the data is anything but 'false', its True. Otherwise, True.

    Returns:
        Boolean of whether the server is online-mode or not
    """
    if not server_properties_file_path.exists():
        logger.debug(f"'{server_properties_file_path}' does not exist, returning True")
        return True

    server_properties_data = properties.loads(server_properties_file_path.read_text())["data"]
    server_online_mode = server_properties_data.get("online-mode")
    if server_online_mode is None:
        logger.debug(f"'{server_properties_file_path}' does not have 'online_mode', returning True")
        return True

    online_mode = server_online_mode != "false"
    logger.debug(f"'server_online_mode' is '{server_online_mode}', returning {online_mode}")
    return online_mode