#Modules
# Standard
import json

# MCServer
from .shared import modrinth_dir

#Variables
_slug_index = None

#Paths
slug_index_file = modrinth_dir / "slug_index.json"

#Functions
def _load_slug_index() -> None:
    global _slug_index
    if _slug_index is None:
        _slug_index = json.loads(slug_index_file.read_text())

def slug_to_id(project_slug: str) -> str:
    _load_slug_index()
    project_id: str = ""
    if _slug_index is not None:
        project_id = _slug_index.get(project_slug, project_slug)["id"]

    return project_id

def add_slug(project_slug: str, project_id: str) -> None:
    global _slug_index
    if _slug_index is None:
        _slug_index = {}

    _slug_index[project_slug] = project_id