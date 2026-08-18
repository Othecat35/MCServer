# Modules
# Standard
import json
from typing import TypedDict

# MCServer
from .shared import mcserver_dir


class MCServerMetadata(TypedDict):
    version: str


class Metadata(TypedDict):
    mcserver: MCServerMetadata


# Paths
metadata_file = mcserver_dir / "metadata.json"


# Functions
def set_metadata(mcserver_version: str) -> None:
    metadata: Metadata = {"mcserver": {"version": mcserver_version}}

    metadata_data: str = json.dumps(metadata)
    metadata_file.write_text(metadata_data)


def get_metadata() -> Metadata:
    metadata_data = metadata_file.read_text()
    metadata: Metadata = json.loads(metadata_data)
    return metadata
