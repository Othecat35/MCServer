#Modules
# Standard
import json

import logging as log

# MCServer
from shared import mcserver_dir, merge_dict

#Paths
indexes_dir = mcserver_dir / "indexes"
slug_id_file = indexes_dir / ".slug_id.json"

#Functions
def create_project_index(project_id: str, metadata: dict | None = None, relationship: dict | None = None) -> None:
  if metadata is None: metadata = {}
  if relationship is None: relationship = {}

  project_index = indexes_dir / project_id
  project_metadata = project_index / "metadata.json"
  project_relationship = project_index / "relationship.json"

  if project_index.exists():
    raise FileExistsError(f"Project index for '{project_id}' already exists")

  project_index.mkdir()
  project_metadata.write_text(json.dumps(metadata, indent=2))
  project_relationship.write_text(json.dumps(relationship, indent=2))

def read_project_index(project_id: str) -> dict:
  project_index = indexes_dir / project_id
  project_metadata = project_index / "metadata.json"
  project_relationship = project_index / "relationship.json"

  return {
    "metadata": json.loads(project_metadata.read_text()),
    "relationship": json.loads(project_relationship.read_text())
  }

def update_project_index(project_id: str, new_metadata: dict | None = None, new_relationship: dict | None = None) -> None:
  if new_metadata is None: new_metadata = {}
  if new_relationship is None: new_relationship = {}

  project_index = indexes_dir / project_id
  project_metadata = project_index / "metadata.json"
  project_relationship = project_index / "relationship.json"

  old_data = read_project_index(project_id)
  project_metadata.write_text(json.dumps(merge_dict(old_data["metadata"], new_metadata), indent=2))
  project_relationship.write_text(json.dumps(merge_dict(old_data["relationship"], new_relationship), indent=2))

def delete_project_index(project_id: str) -> None:
  project_index = indexes_dir / project_id
  project_metadata = project_index / "metadata.json"
  project_relationship = project_index / "relationship.json"

  project_metadata.unlink()
  project_relationship.unlink()
  project_index.rmdir()

def project_index_exists(project_id: str) -> bool:
  return (indexes_dir / project_id).exists()

# Slug to ID
slug_id = {}
def slug_to_id(project_slug: str) -> str:
  global slug_id
  if not slug_id:
    log.debug("Loading slug_id.json")
    slug_id = json.loads(slug_id_file.read_text())

  project_id = slug_id.get(project_slug, {"id": project_slug})["id"]
  log.debug(f"Project slug '{project_slug}' is id '{project_id}'")
  return project_id
