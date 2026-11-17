from typing import TypedDict

from .shared import Hashes


class LoaderVersion(TypedDict):
    maven_coordinate: str
    version: str
    """The version for this loader release."""
    build_number: int
    """The build number of the loader"""
    version_separator: str
    """The separator used in the loader version"""
    file_size: int
    """The size of the file in bytes"""
    hashes: Hashes