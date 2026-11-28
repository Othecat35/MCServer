import logging

from .. import paths
from . import properties

logger = logging.getLogger(__name__)


def get_online_mode() -> bool:
    """Get the online mode of the server
    If the file does not exists, its True. If it does exist but it doesn't have the online-mode, its
    True. If it does have online-mode, but the data is anything but 'false', its True. Otherwise, True.

    Returns:
        Boolean of whether the server is online-mode or not
    """
    if not paths.server_properties_file.exists():
        logger.debug(
            f"'{paths.server_properties_file}' does not exist, returning True for online-mode"
        )
        return True

    server_properties_data = properties.loads(paths.server_properties_file.read_text())[
        "data"
    ]
    server_online_mode = server_properties_data.get("online-mode")
    if server_online_mode is None:
        logger.debug(
            f"'{paths.server_properties_file}' does not have 'online_mode', returning True"
        )
        return True

    online_mode = server_online_mode != "false"
    logger.debug(
        f"'server_online_mode' is '{server_online_mode}', returning {online_mode}"
    )
    return online_mode


def get_operator_permission_level() -> int:
    if not paths.server_properties_file.exists():
        logger.debug(
            f"'{paths.server_properties_file}' does not exist, returning 4 for op-permission-level"
        )
        return 4

    server_properties_data = properties.loads(paths.server_properties_file.read_text())[
        "data"
    ]
    server_op_permission_level = server_properties_data.get("op-permission-level")
    if server_op_permission_level is None:
        logger.debug(
            f"'{paths.server_properties_file}' does not have 'server_op_permission_level', returning 4 for op-permission-level"
        )
        return 4

    logger.debug(f"'op-permission-level' is '{server_op_permission_level}'")
    return int(server_op_permission_level)
