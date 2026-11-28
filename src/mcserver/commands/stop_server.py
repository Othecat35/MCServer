import logging
import os
from argparse import Namespace
from signal import SIGTERM

from .. import paths, state

logger: logging.Logger = logging.getLogger(__name__)


def stop_server(args: Namespace) -> int:
    paths.update_working_dir(args.directory)
    current_state = state.get_state()
    if not current_state["is_active"]:
        logger.error("Server is not running.")
        return 1

    if "process_id" not in current_state:
        logger.info("Process ID is not in state file")
        return 1

    logger.info(f"Sending Sigterm to prpcess ID {current_state['process_id']}")
    os.kill(current_state["process_id"], SIGTERM)
    return 0
