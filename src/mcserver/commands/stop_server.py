from argparse import Namespace


def main(args: Namespace) -> int:
    # CLI arguments
    force_stop: bool = args.force_stop

    import logging as log
    import os
    import time
    from signal import SIGKILL, SIGTERM

    from .. import state

    try:
        current_state = state.get_state()
    except FileNotFoundError:
        log.error(f"File '{state.state_file}' not found; MCServer not initialized.")
        return 1

    if not current_state["is_active"]:
        log.error("Server is not running.")
        return 1

    if "process_id" not in current_state:
        log.info("Process ID is not in state file")
        return 1

    log.info(f"Sending Sigterm to prpcess ID {current_state['process_id']}")
    os.kill(current_state["process_id"], SIGTERM)
    return 0
