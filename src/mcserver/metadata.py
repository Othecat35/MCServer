# Modules
# Standard
import json
from typing import TypedDict

# MCServer
from .paths import metadata_file

metadata_format_version = 1

class MetadataFormatVersionError(Exception): pass

class MCServerMetadata(TypedDict):
    version: str


class Metadata(TypedDict):
    format_version: int
    mcserver: MCServerMetadata


# Functions
def set_metadata(mcserver_version: str) -> None:
    metadata: Metadata = {"format_version": metadata_format_version,"mcserver": {"version": mcserver_version}}

    metadata_data: str = json.dumps(metadata)
    metadata_file.write_text(metadata_data)


def get_metadata() -> Metadata:
    metadata_data = metadata_file.read_text()
    metadata: Metadata = json.loads(metadata_data)
    if metadata["format_version"] > metadata_format_version:
        raise MetadataFormatVersionError("Existing metadata format version is higher than current metadata format version")
    return metadata
