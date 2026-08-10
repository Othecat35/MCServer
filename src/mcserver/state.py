# Modules
# Standard
import json
import logging as log
import os
from pathlib import Path
from typing import TypedDict

# MCServer
from .shared import mcserver_dir


# TypedDict
class State(TypedDict):
    process_id: int
    start_time: int
    action: str


class CurrentState(TypedDict):
    is_active: bool
    process_id: int
    start_time: int
    action: str


# Paths
proc_dir = Path("/proc")
state_file = mcserver_dir / "state.json"


# Functions
def get_start_time(process_id: int | str) -> int:
    process_id = str(process_id)

    proc_pid = proc_dir / process_id
    if not proc_pid.exists():
        log.debug(f"Process ID ({process_id}) does not exist")
        return 0

    pid_stat = proc_pid / "stat"
    pid_stat_data = pid_stat.read_text()

    start_time: int = int(pid_stat_data.split()[21])
    return start_time


def set_state(action: str) -> None:
    current_state: State = {
        "process_id": os.getpid(),
        "start_time": get_start_time("self"),
        "action": action,
    }

    state_data: str = json.dumps(current_state, indent=2)
    state_file.write_text(state_data)


def get_state() -> CurrentState:
    state_data: str = state_file.read_text()
    file_state: State = json.loads(state_data)  # I ran out of naming

    current_state: CurrentState = {
        "is_active": False,
        "process_id": file_state["process_id"],
        "start_time": file_state["start_time"],
        "action": file_state["action"],
    }

    if file_state["start_time"] == get_start_time(file_state["process_id"]):
        current_state["is_active"] = True

    return current_state


def clear_state() -> None:
    state_file.write_text(json.dumps({}))
