from argparse import Namespace


def stop(args: Namespace) -> int:
    import logging as log
    import os
    from signal import SIGTERM

    from .. import state

    current_state = state.get_state()
    if not current_state["is_active"]:
        log.error("Server is not running.")
        return 1

    if "process_id" not in current_state:
        log.info("Process ID is not in state file")
        return 1

    log.info(f"Sending Sigterm to prpcess ID {current_state['process_id']}")
    os.kill(current_state["process_id"], SIGTERM)
    return 0
