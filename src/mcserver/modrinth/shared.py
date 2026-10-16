# Modules
# Standard
from pathlib import Path
from typing import Literal, TypeAlias

# MCServer
from ..shared import mcserver_dir

# TypeAliases
DependencyType: TypeAlias = Literal["embedded", "optional", "required", "incompatible"]
ProjectSide: TypeAlias = Literal["required", "optional", "unsupported", "unknown"]
ProjectEnvironment: TypeAlias = Literal[
    "client_and_server",
    "client_only",
    "client_only_server_optional",
    "singleplayer_only",
    "server_only",
    "server_only_client_optional",
    "dedicated_server_only",
    "client_or_server",
    "client_or_server_prefers_both",
    "unknown",
]

SearchSortIndex: TypeAlias = Literal[
    "relevance", "downloads", "follows", "newest", "updated"
]

# Variables
modrinth_dir: Path = mcserver_dir / "modrinth"
project_records_dir: Path = modrinth_dir / "project_records"
search_sort_index: list[str] = [
    "relevance",
    "downloads",
    "follows",
    "newest",
    "updated",
]
