# Modules
# Standard
import json
import logging as log
from datetime import UTC, datetime, timedelta
from typing import TypedDict

# MCServer
from ..paths import mcserver_cache_dir


# TypedDict
class SlugIndex(TypedDict):
    project_id: str
    last_updated_time: str  # ISO-8601


# Variables
_slug_index: dict[str, SlugIndex] | None = None

# Paths
slug_index_file = mcserver_cache_dir / "slug_index.json"


# Functions
def _load_slug_index() -> None:
    global _slug_index
    if _slug_index is not None:
        log.debug("Not loading _slug_index; _slug_index is not 'None'")
        return

    if not slug_index_file.exists():
        log.debug(
            f"{slug_index_file} does not exist, setting _slug_index to empty dictionary"
        )
        _slug_index = {}
        return

    slug_index_json = slug_index_file.read_text()

    try:
        _slug_index = json.loads(slug_index_json)
        if not isinstance(_slug_index, dict):
            log.warning(
                f"{slug_index_file} should be an object! Rebuilding it from scratch"
            )  # that's all I can say.
            _slug_index = {}
    except json.JSONDecodeError:
        log.warning(
            f"{slug_index_file} is corrupted! Rebuilding it from scratch"
        )  # that's all I can say.
        _slug_index = {}


def is_index_outdated(project_slug: str) -> bool:
    _load_slug_index()

    if _slug_index is None:
        log.debug(
            "Slug index is 'None'"
        )  # well, idk how can this get triggered even though _load_slug_index at least set it to {}
        return True

    slug_index = _slug_index.get(project_slug)
    if slug_index is None:
        log.debug(f"Project slug ({project_slug}) is not known yet")
        return True

    last_updated_time = slug_index.get("last_updated_time")
    if last_updated_time is None:
        return True

    try:
        last_updated = datetime.fromisoformat(last_updated_time)
    except ValueError:
        log.debug("Invalid ISO formatted time, do not mess with it pls")
        return True

    time_now = datetime.now(tz=UTC)
    time_to_live = timedelta(days=7)
    return time_now - last_updated > time_to_live


def slug_to_id(project_slug: str) -> str:
    if is_index_outdated(project_slug):
        return project_slug

    global _slug_index
    project_id: str = ""
    if _slug_index is None:
        _slug_index = {}

    slug_index = _slug_index.get(project_slug)
    if slug_index is None:
        return project_slug

    project_id = slug_index.get("project_id")
    if (
        project_id is None
    ):  # even though pyright thinks this code is unreachable, we can't trust the user
        return project_slug

    return project_id


def update_slug_index(project_slug: str, project_id: str):
    _load_slug_index()

    global _slug_index
    if _slug_index is None:
        _slug_index = {}

    slug_index: SlugIndex = {
        "project_id": project_id,
        "last_updated_time": datetime.now(tz=UTC).isoformat(),
    }

    _slug_index[project_slug] = slug_index


def save_slug_index() -> None:
    global _slug_index
    if _slug_index is None:
        _slug_index = {}

    _slug_index_json = json.dumps(_slug_index)
    mcserver_cache_dir.mkdir(parents=True, exist_ok=True)
    slug_index_file.write_text(_slug_index_json)
