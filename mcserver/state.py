#Modules
# Standard
import json, os

import logging as log

from pathlib import Path

# MCServer
from shared import mcserver_dir

# Paths
state_file = mcserver_dir / "state.json"

# Functions
def get_start_time(pid: int | str) -> int:
  proc_path = Path("/proc") / str(pid)
  if not proc_path.exists():
    log.debug(f"Process ID ({pid}) seems not exist")
    return 0

  return int((proc_path / "stat").read_text().split()[21])

def get_state() -> dict:
  if not state_file.exists():
    state_file.write_text(json.dumps({}))

  return json.loads(state_file.read_text())

def is_active() -> bool:
  current_state = get_state()
  if not current_state:
    return False
  elif current_state["start_time"] == get_start_time(current_state["process_id"]):
    return True

  return False

def set_state(action: str) -> None:
  state_data = {
    "process_id": os.getpid(),
    "start_time": get_start_time("self"),
    "action": action
  }

  state_file.write_text(json.dumps(state_data, indent=2))
