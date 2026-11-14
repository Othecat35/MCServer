# Modules
# Standard
import json
import logging
from datetime import UTC, datetime, timedelta
from typing import TypedDict

# MCServer
from .. import shared
from ..paths import mcserver_cache_dir

logger = logging.getLogger(__name__)


# TypedDict
class SlugIndex(TypedDict):
    project_id: str
    last_updated: str  # ISO-8601

class SlugIndexData(TypedDict):
    format_version: int
    data: dict[str, SlugIndex]


# Variables
_slug_index: dict[str, SlugIndex] | None = None
format_version = 1

# Paths
slug_index_file = mcserver_cache_dir / "slug_index.json"


# Functions
def _load_slug_index() -> None:
    global _slug_index
    if _slug_index is not None:
        logger.debug("Slug index is already set, not reloading")
        return

    if not slug_index_file.exists():
        logger.debug(
            f"{slug_index_file} does not exist, setting _slug_index to empty dictionary"
        )
        _slug_index = {}
        return

    slug_index_json = slug_index_file.read_text()

    try:
        slug_index_data = json.loads(slug_index_json)
        if not isinstance(slug_index_data, dict):
            logger.warning(
                f"{slug_index_file} should be an object! Rebuilding it from scratch"
            )  # that's all I can say.
            _slug_index = {}
            return

        if slug_index_data.get("format_version") is None:
            logger.debug("Let's throw this slug_index that doesn't have format_version")
            _slug_index = {}
            return

        _slug_index = slug_index_data["data"]
    except json.JSONDecodeError:
        logger.warning(
            f"{slug_index_file} is corrupted! Rebuilding it from scratch"
        )  # that's all I can say.
        _slug_index = {}

    logger.debug("Loaded slug index from file")


def is_index_outdated(project_slug: str) -> bool:
    _load_slug_index()

    if _slug_index is None:
        logger.debug(
            "Slug index is 'None'"
        )  # well, idk how can this get triggered even though _load_slug_index at least set it to {}
        return True

    slug_index = _slug_index.get(project_slug)
    if slug_index is None:
        logger.debug(f"Project slug ({project_slug}) is not known yet")
        return True

    last_updated_time = slug_index.get("last_updated")
    if last_updated_time is None:
        return True

    try:
        last_updated = datetime.fromisoformat(last_updated_time)
    except ValueError:
        logger.debug("Invalid ISO formatted time, do not mess with it pls")
        return True

    time_now = datetime.now(tz=UTC)
    time_to_live = timedelta(days=7)
    return time_now - last_updated > time_to_live


def slug_to_id(project_slug: str) -> str:
    _load_slug_index()
    global _slug_index
    if _slug_index is None:
        logger.debug("Idk how _slug_index can be None")
        _slug_index = {}

    if project_slug not in _slug_index:
        logger.debug(f"Project slug '{project_slug}' is not in the index")
        return project_slug

    slug_index = _slug_index[project_slug]
    if "project_id" not in slug_index:
        logger.debug(f"Project slug '{project_slug}' does not have 'project_id'")
        return project_slug

    project_id = slug_index["project_id"]
    logger.debug(f"Project slug {project_slug} is project ID {project_id}")
    return project_id


def update_slug_index(project_slug: str, project_id: str):
    _load_slug_index()

    global _slug_index
    if _slug_index is None:
        _slug_index = {}

    slug_index: SlugIndex = {
        "project_id": project_id,
        "last_updated": datetime.now(tz=UTC).isoformat(),
    }

    _slug_index[project_slug] = slug_index
    logger.debug(f"Updated slug index for project slug {project_slug} to project ID {project_id}")


def save_slug_index() -> None:
    if _slug_index is None:
        logger.debug("Slug index is not set")
        return

    mcserver_cache_dir.mkdir(parents=True, exist_ok=True)

    logger.debug("Saving slug index to file")
    slug_index_data: SlugIndexData = {
        "format_version": 1,
        "data": _slug_index
    }

    shared.update_file(slug_index_file, json.dumps(slug_index_data).encode())
