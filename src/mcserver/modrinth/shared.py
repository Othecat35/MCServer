# Modules
# Standard
from pathlib import Path
from typing import Literal, TypeAlias

# MCServer
from ..shared import mcserver_dir

# TypeAliases
DependencyTypes: TypeAlias = Literal["embedded", "optional", "required", "incompatible"]
ProjectEnvironments: TypeAlias = Literal[
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

# Variables
modrinth_dir: Path = mcserver_dir / "modrinth"
