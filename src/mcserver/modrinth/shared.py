# Modules
# Standard
from pathlib import Path
from typing import Literal, TypeAlias

# MCServer
from ..shared import mcserver_dir

#TypeAliases
DependencyTypes: TypeAlias = Literal["embedded", "optional", "required", "incompatible"]

# Variables
modrinth_dir: Path = mcserver_dir / "modrinth"