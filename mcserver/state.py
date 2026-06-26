#Modules
# Standard
import json, os, sys

from pathlib import Path

# MCServer
from shared import mcserver_dir

# Paths
state_file = mcserver_dir / "state.json"

# Functions
def get_start_time(pid: int | str) -> int:
  return int((Path("/proc") / str(pid) / "stat").read_text().split()[21])

def get_state() -> dict:
  return json.loads(state_file.read_text())

def is_active():
  current_state = get_state()
  if not current_state:
    return False
  elif current_state.get("start_time", 0) != get_start_time(current_state["process_id"]):
    return True

  return False

def set_state():
  state_data = {
    "process_id": os.getpid(),
    "start_time": get_start_time("self")
  }

  state_file.write_text(json.dumps(state_data, indent=2))
