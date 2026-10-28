from typing import Literal, NotRequired, TypedDict

from .shared import Environment

type DependencyType = Literal["required", "optional", "incompatible", "embedded"]
type FileType = Literal[
    "required-resource-pack",
    "optional-resource-pack sources-jar",
    "dev-jar",
    "javadoc-jar",
    "unknown",
    "signature",
]
type RequestedVersionStatus = Literal["listed", "archived", "draft", "unlisted"]
type VersionStatus = Literal[
    "listed", "archived", "draft", "unlisted", "scheduled", "unknown"
]
type VersionType = Literal["release", "beta", "alpha"]


class Dependency(TypedDict):
    version_id: NotRequired[str | None]
    """The ID of the version that this version depends on"""
    project_id: NotRequired[str | None]
    """The ID of the project that this version depends on"""
    file_name: NotRequired[str | None]
    """The file name of the dependency, mostly used for showing external dependencies on modpacks"""
    dependency_type: DependencyType
    """The type of dependency that this version has"""


class FileHashes(TypedDict):
    sha512: NotRequired[str]
    """No description from Modrinth ;-;"""
    sha1: NotRequired[str]
    """No description from Modrinth ;-;"""


class File(TypedDict):
    file_hashes: FileHashes
    """A map of hashes of the file. The key is the hashing algorithm and the value is the string version of the hash."""
    download_url: str
    """A direct link to the file"""
    file_name: str
    """The name of the file"""
    is_primary: bool
    """Whether this file is the primary one for its version. Only a maximum of one file per version will have this set to true. If there are not any primary files, it can be inferred that the first file is the primary one."""
    file_size: int
    """The size of the file in bytes"""
    file_type: NotRequired[FileType | None]
    """No description from Modrinth ;-;"""


class ProjectVersion(TypedDict):
    version_name: NotRequired[str]
    """The name of this version"""
    version_number: NotRequired[str]
    """The version number. Ideally will follow semantic versioning"""
    changelog: NotRequired[str | None]
    """The changelog for this version"""
    dependencies: NotRequired[list[Dependency]]
    """A list of specific versions of projects that this version depends on"""
    game_versions: NotRequired[list[str]]
    """A list of versions of Minecraft that this version supports"""
    version_type: NotRequired[VersionType]
    """The release channel for this version"""
    loader_names: NotRequired[list[str]]
    """The mod loaders that this version supports. In case of resource packs, use “minecraft”"""
    is_featured: NotRequired[bool]
    """Whether the version is featured or not"""
    version_status: NotRequired[VersionStatus]
    """No description from Modrinth ;-;"""
    requested_version_status: NotRequired[RequestedVersionStatus | None]
    """No description from Modrinth ;-;"""
    version_id: str
    """The ID of the version, encoded as a base62 string"""
    project_id: str
    """The ID of the project this version is for"""
    author_id: str
    """The ID of the author who published this version"""
    published_time: str
    """No description from Modrinth ;-; (format: ISO-8601)"""
    download_count: int
    """The number of times this version has been downloaded"""
    changelog_url: NotRequired[str | None]
    """A link to the changelog for this version. Always null, only kept for legacy compatibility."""
    environment: Environment
    """The environment a project or version supports. For an explanation of each environment, see the blog post here: https://modrinth.com/news/article/new-environments/#new-system"""
    files: list[File]
    """A list of files available for download for this version"""
