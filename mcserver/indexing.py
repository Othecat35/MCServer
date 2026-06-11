import json

import logging as log

from shared import mcserver_dir

# Variables
project_indexes_dir = mcserver_dir / "project_indexes"
slug_id_file = project_indexes_dir / ".slug_id.json"

# Functions
def project_index_exists(project_id: str) -> bool:
  return (project_indexes_dir / f"{project_id}.json").exists()

def write_project_index(project_id: str, project_data: dict) -> None:
  (project_indexes_dir / f"{project_id}.json").write_text(json.dumps(project_data, indent=2))

def read_project_index(project_id: str) -> dict:
  return json.loads((project_indexes_dir / f"{project_id}.json").read_text())

def create_project_index(project_id: str, project_data: dict) -> None:
  if project_index_exists(project_id):
    raise FileExistsError(f"Project index file for '{project_id}' already exists")
  else:
    write_project_index(project_id, project_data)

slug_id = {}
def slug_to_id(project_slug: str) -> str:
  global slug_id
  if not slug_id:
    log.debug("Loading slug_id.json")
    slug_id = json.loads(slug_id_file.read_text())

  project_id = slug_id.get(project_slug, project_slug)
  log.debug(f"Project slug '{project_slug}' is id '{project_id}'")
  return project_id
