# Modules
# Standard
import json
import logging
import os
from pathlib import Path
from typing import Literal, NotRequired, TypedDict

# MCServer
from .paths import proc_dir, state_file

logger: logging.Logger = logging.getLogger(__name__)

type MCServerActions = Literal["initializing_server", "server_running"]


# TypedDict
class State(TypedDict):
    process_id: int
    start_time: int
    action: MCServerActions


class CurrentState(TypedDict):
    is_active: bool
    process_id: NotRequired[int]
    start_time: NotRequired[int]
    action: NotRequired[str]


# Functions
def get_start_time(process_id: int | str) -> int:
    process_id = str(process_id)

    proc_pid: Path = proc_dir / process_id
    if not proc_pid.exists():
        raise FileNotFoundError(f"/proc does not have process ID '{process_id}'")

    pid_stat_file: Path = proc_pid / "stat"
    pid_stat_data: str = pid_stat_file.read_text()

    last_close_parenthesis: int = pid_stat_data.rfind(")")
    remaining_fields: list[str] = (
        pid_stat_data[last_close_parenthesis + 1 :].strip().split()
    )
    start_time: int = int(remaining_fields[19])
    return start_time


def set_state(action: MCServerActions) -> None:
    current_state: State = {
        "process_id": os.getpid(),
        "start_time": get_start_time("self"),
        "action": action,
    }

    state_data: str = json.dumps(current_state, indent=2)
    state_file.write_text(state_data)

def get_state() -> CurrentState:
    current_state: CurrentState = {"is_active": False}

    if not state_file.exists():
        logger.debug("State file does not exist")
        return current_state

    state_data: str = state_file.read_text()
    file_state: State = json.loads(state_data)  # I ran out of naming

    if "action" in file_state:
        current_state["action"] = file_state["action"]

    if "process_id" in file_state:
        current_state["process_id"] = file_state["process_id"]
    else:
        return current_state

    if "start_time" in file_state:
        current_state["start_time"] = file_state["start_time"]
    else:
        return current_state

    if file_state["start_time"] == get_start_time(file_state["process_id"]):
        current_state["is_active"] = True

    return current_state
