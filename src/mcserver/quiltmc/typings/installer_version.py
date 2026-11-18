from typing import TypedDict

from .shared import Hashes


class InstallerVersion(TypedDict):
    maven_coordinate: str
    version_string: str
    download_url: str
    file_size: int
    hashes: Hashes #idk what this represents
