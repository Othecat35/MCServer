# Modules
# Standard
from datetime import datetime, timedelta, timezone
import json
import time
import logging as log
from typing import TypedDict

# MCServer
from ..paths import mcserver_cache_dir

# TypedDict
class SlugIndex(TypedDict):
    project_id: str
    last_updated_time: str # ISO-8601

# Variables
_slug_index: dict[str, SlugIndex] | None = None

# Paths
slug_index_file = mcserver_cache_dir / "slug_index.json"

# Functions
def _load_slug_index() -> None:
    global _slug_index
    if _slug_index is not None:
        log.debug("Not loading slug index; slug index is not none")
        return

    if not slug_index_file.exists():
        log.debug(f"{slug_index_file} does not exist, setting slug_index to empty dictionary")
        _slug_index = {}
        return

    slug_index_json = slug_index_file.read_text()

    try:
        _slug_index = json.loads(slug_index_json)
    except json.JSONDecodeError:
        log.warning(f"{slug_index_file} is corrupted") # that's all I can say.
        _slug_index = {}


def is_index_expired(project_slug: str) -> bool:
    _load_slug_index()

    global _slug_index
    if _slug_index is None:
        log.debug("Slug index is none (idk how that happens despite we called load_slug_index first)")
        return True

    slug_index = _slug_index.get(project_slug)
    if slug_index is None:
        log.debug("Project slug is not indexed yet")
        return True
    
    last_updated_time = slug_index.get("last_updated_time")
    if last_updated_time is None:
        return True
    
    time_now = datetime.now()
    last_updated = datetime.fromisoformat(last_updated_time)
    time_to_live = timedelta(days=7)
    if last_updated - time_now > time_to_live:
        return True

    return False


def slug_to_id(project_slug: str) -> str:
    if is_index_expired(project_slug):
        return project_slug

    _load_slug_index()

    global _slug_index
    project_id: str = ""
    if _slug_index is None:
        _slug_index = {}

    slug_index = _slug_index.get(project_slug)
    if slug_index is None:
        return project_slug

    project_id = slug_index.get("project_id")
    if project_id is None:
        return project_slug

    return project_id


def add_slug(project_slug: str, project_id: str) -> None:
    _load_slug_index()

    global _slug_index
    if _slug_index is None:
        _slug_index = {}

    slug_index: SlugIndex = {
        "project_id": project_id,
        "last_updated_time": datetime.now(tz=timezone.utc).isoformat()
    }

    _slug_index[project_slug] = slug_index

def update_slug_index(project_slug: str, project_id: str):
    pass

def save_slug_index() -> None:
    global _slug_index
    if _slug_index is None:
        _slug_index = {}

    _slug_index_json = json.dumps(_slug_index)
    slug_index_file.write_text(_slug_index_json)
    _slug_index = None
