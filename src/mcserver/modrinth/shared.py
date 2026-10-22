# Modules
# Standard
from typing import Literal, NotRequired, TypeAlias, TypedDict, get_args

from .typings import (
    Environment,
    EnvironmentSide,
    MonetizationStatus,
    ProjectStatus,
    ProjectType,
)

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
class ProjectLicense(TypedDict):
    license_id: NotRequired[str]
    """The SPDX license ID of a project"""
    license_name: NotRequired[str]
    """The long name of a license"""
    license_url: NotRequired[str | None]
    """The URL to this license"""


class DonationPlatforms(TypedDict):
    donation_id: NotRequired[str]


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
search_sort_index: list[str] = [
    "relevance",
    "downloads",
    "follows",
    "newest",
    "updated",
]

ENVIRONMENT: frozenset[str] = frozenset(get_args(Environment.__value__))
ENVIRONMENT_SIDE: frozenset[str] = frozenset(get_args(EnvironmentSide.__value__))
MONETIZATION_STATUS: frozenset[str] = frozenset(get_args(MonetizationStatus.__value__))
PROJECT_STATUS: frozenset[str] = frozenset(get_args(ProjectStatus.__value__))
PROJECT_TYPE: frozenset[str] = frozenset(get_args(ProjectType.__value__))
