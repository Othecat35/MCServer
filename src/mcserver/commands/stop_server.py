from argparse import Namespace as argparseNamespace
def main(args: argparseNamespace) -> int:
    # CLI arguments
    force_stop: bool = args.force_stop

    import os
    import logging as log
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

    log.info("Stopping server...")
    os.kill(current_state["process_id"], SIGTERM)

    current_state = state.get_state()
    if current_state["is_active"]:
        return 0

    if not force_stop:
        log.warning("Server appears to still be running, you may stop the server manually.")
        return 1

    import time
    from .. import config
    launcher_config = config.load_config("launcher")
    time.sleep(launcher_config["force_stop"])

    log.warning("Server process is still running, force stopping the server...")
    os.kill(current_state["process_id"], SIGKILL)
    return 1
