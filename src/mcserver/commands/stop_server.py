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

    log.info("Stopping server...")
    os.kill(current_state["process_id"], SIGTERM)

    time.sleep(1)

    current_state = state.get_state()
    if not current_state["is_active"]:
        return 0

    if not force_stop:
        log.warning(
            "Server appears to still be running, you may stop the server manually."
        )
        return 1

    from .. import config

    launcher_config = config.load_config("launcher")
    force_stop_timeout = launcher_config["force_stop"]
    log.warning(
            f"Server appears to still be running, force stopping the server in {force_stop_timeout} seconds..."
        )
    time.sleep(force_stop_timeout)

    current_state = state.get_state()
    if not current_state["is_active"]:
        return 0

    if "process_id" not in current_state:
        log.info("Process ID is not in state file")
        return 1

    log.warning("Force stopping the server...")
    os.kill(current_state["process_id"], SIGKILL)
    return 1
