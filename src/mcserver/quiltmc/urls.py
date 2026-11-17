import importlib
import logging
from types import SimpleNamespace
from typing import TypedDict

logger = logging.getLogger(__name__)

class GlobalURLsModule(TypedDict):
    name: str
    package: str | None

global_urls: GlobalURLsModule = {
    "name": "..config",
    "package": __package__
}

try:
    urls = importlib.import_module(global_urls["name"], global_urls["package"])
except ImportError:
    logger.debug(f"Module name '{global_urls['name']}' package '{global_urls['package']}' does not exist, using default values")
    urls = SimpleNamespace()

quiltmc_api_url: str = getattr(urls, "quiltmc_api_url", "https://meta.quiltmc.org")
