# Modules
# Standard
from pathlib import Path
from typing import Literal, NotRequired, TypedDict, TypeAlias

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


# TypedDict
class FileHashes(TypedDict):
    sha512: NotRequired[str]
    sha1: NotRequired[str]


class VersionFile(TypedDict):
    file_hashes: FileHashes
    """A map of hashes of the file. The key is the hashing algorithm and the value is the string version of the hash."""
    download_url: str
    """A direct link to the file"""
    filename: str
    """The name of the file"""
    is_primary: bool
    """Whether this file is the primary one for its version. Only a maximum of one file per version will have this set to true. If there are not any primary files, it can be inferred that the first file is the primary one."""
    file_size: int
    """The size of the file in bytes"""
    file_type: NotRequired[
        Literal[
            "required-resource-pack",
            "optional-resource-pack",
            "sources-jar",
            "dev-jar",
            "javadoc-jar",
            "unknown",
            "signature",
        ]
        | None
    ]
    file_id: NotRequired[str | None]
    """UNDOCUMENTED!"""


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
