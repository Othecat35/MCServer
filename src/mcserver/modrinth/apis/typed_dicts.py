from typing import Literal, NotRequired, TypedDict

from ..shared import DependencyTypes, ProjectEnvironments


# Project Version
class VersionDependency(TypedDict):
    version_id: NotRequired[str | None]
    """The ID of the version that this version depends on"""
    project_id: NotRequired[str | None]
    """The ID of the project that this version depends on"""
    filename: NotRequired[str | None]
    """The file name of the dependency, mostly used for showing external dependencies on modpacks"""
    dependency_type: DependencyTypes
    """The type of dependency that this version has"""


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


class ProjectVersion(TypedDict):
    version_name: NotRequired[str]
    """The name of this version"""
    version_number: NotRequired[str]
    """The version number. Ideally will follow semantic versioning"""  # No it does not
    changelog: NotRequired[str | None]
    """The changelog for this version"""
    dependencies: NotRequired[list[VersionDependency]]
    """A list of specific versions of projects that this version depends on"""
    game_versions: NotRequired[list[str]]
    """A list of versions of Minecraft that this version supports"""
    version_type: NotRequired[Literal["release", "beta", "alpha"]]
    """The release channel for this version"""
    loader_names: NotRequired[list[str]]
    """The mod loaders that this version supports. In case of resource packs, use 'minecraft'"""
    is_featured: NotRequired[bool]
    """Whether the version is featured or not"""
    status: NotRequired[
        Literal["listed", "archived", "draft", "unlisted", "scheduled", "unknown"]
    ]
    requested_status: NotRequired[
        Literal["listed", "archived", "draft", "unlisted"] | None
    ]
    version_id: str
    """The ID of the version, encoded as a base62 string"""
    project_id: str
    """The ID of the project this version is for"""
    author_id: str
    """The ID of the author who published this version"""
    published_time: str  # Time format: ISO-8601
    download_count: int
    """The number of times this version has been downloaded"""
    changelog_url: NotRequired[str | None]
    """A link to the changelog for this version. Always null, only kept for legacy compatibility."""
    environment: ProjectEnvironments
    """The environment a project or version supports. For an explanation of each environment, see the blog post here: https://modrinth.com/news/article/new-environments/#new-system"""
    files: list[VersionFile]


# Project Information
class DonationPlatform(TypedDict):
    platform_id: NotRequired[str]
    platform_name: NotRequired[str]
    donation_url: NotRequired[str]


class ModeratorMessage(TypedDict):
    message: NotRequired[str]
    body: NotRequired[str | None]


class ProjectLicense(TypedDict):
    license_id: NotRequired[str]
    license_name: NotRequired[str]
    license_url: NotRequired[str | None]


class GalleryImage(TypedDict):
    image_url: str
    is_featured: bool
    image_title: NotRequired[str | None]
    image_description: NotRequired[str | None]
    created_time: str  # Time format: ISO-8601
    image_order: NotRequired[int]


class ProjectInformation(TypedDict):
    project_slug: NotRequired[str]
    project_title: NotRequired[str]
    summary: NotRequired[str]
    categories: NotRequired[list[str]]
    client_side: DependencyTypes
    server_side: DependencyTypes
    description: NotRequired[str]
    status: NotRequired[
        Literal[
            "approved",
            "archived",
            "rejected",
            "draft",
            "unlisted",
            "processing",
            "withheld",
            "scheduled",
            "private",
            "unknown",
        ]
    ]
    requested_status: NotRequired[
        Literal["approved", "archived", "unlisted", "private", "draft"] | None
    ]
    additional_categories: NotRequired[list[str]]
    issues_url: NotRequired[str | None]
    source_url: NotRequired[str | None]
    wiki_url: NotRequired[str | None]
    discord_url: NotRequired[str | None]
    donation_platforms: NotRequired[list[DonationPlatform]]
    project_type: Literal["mod", "modpack", "resourcepack", "shader"]
    download_count: int
    icon_url: NotRequired[str | None]
    icon_color: NotRequired[int | None]
    thread_id: NotRequired[str]
    monetization_status: NotRequired[
        Literal["monetized", "demonetized", "force-demonetized"]
    ]
    project_id: str
    team_id: str
    description_url: NotRequired[str | None]
    moderator_message: NotRequired[
        ModeratorMessage | None
    ]  # NOTE: The docs is misleading
    published_time: str  # Time format: ISO-8601
    last_updated_time: str  # Time format: ISO-8601
    approved_time: NotRequired[str | None]  # Time format: ISO-8601
    queued_time: NotRequired[str | None]  # Time format: ISO-8601
    follower_count: int
    license: NotRequired[ProjectLicense]
    version_ids: NotRequired[list[str]]
    game_versions: NotRequired[list[str]]
    loader_names: NotRequired[list[str]]
    project_gallery: NotRequired[list[GalleryImage]]


class SearchHit(TypedDict):
    project_id: str
    """The ID of the project, encoded as a base62 string"""
    project_type: Literal["mod", "modpack", "resourcepack", "shader"]
    """The project type of the project"""
    all_project_types: list[
        Literal["mod", "resourcepack", "datapack", "shader", "modpack", "plugin"]
    ]
    """All project types across every version of the project, unlike project_type which only reflects a version-specific type"""
    project_title: str
    """The title or name of the project"""
    short_description: str
    """A short sentence summarizing the project, no more than a sentence or two."""
    author_username: str
    """The username of the project's author"""
    categories: list[str]
    """A list of the featured categories that the project has."""
    display_categories: list[str]
    """A list of the featured categories that the project has. Equivalent to categories on the project itself."""
    minecraft_versions: list[str]
    """A list of the minecraft versions supported by the project"""
    download_count: int
    """The total number of downloads of the project"""
    follow_count: int
    """The total number of users following the project"""
    icon_url: str
    """The URL of the project's icon"""
    created_time: str  # Time Format: ISO-8601
    """The date the project was created"""
    last_modified_time: str  # Time Format: ISO-8601
    """The date the latest version of the project was created"""
    latest_version_id: str
    """The ID of the latest version of the project"""
    license_id: str
    """The SPDX license ID of a project"""
    project_environment: ProjectEnvironments  # For plugin it is almost certainly always be server-only, but whatever I can't assume
    """All the environments that versions of this project support. Not in any particular order, we recommend using the environment information on a version instead. For an explanation of each environment, see the blog post here: https://modrinth.com/news/article/new-environments/#new-system"""
    disclosure_type: list[
        Literal[
            "ai_content",
            "ai_content_code",
            "ai_content_assets",
            "ai_content_text",
            "ai_content_functionality",
            "advertisements",
            "epilepsy_triggers",
            "system_interactions",
            "telemetry",
            "telemetry_opt_in",
            "telemetry_opt_out",
            "telemetry_always_active",
            "derivative_work",
            "paid_features",
            "archived",
        ]
    ]
    """Disclosures listed on the project."""
    gallery_image_urls: list[str]
    """A list of images that have been uploaded to the project's gallery"""
    project_slug: NotRequired[str | None]
    """The slug of a project, used for vanity URLs. Regex: ^[\\w!@$()`.+,"\\-']{3,64}$"""
    author_id: NotRequired[str | None]
    """The ID of the project’s author"""
    organization_name: NotRequired[str | None]
    """The name of the organization that owns this project"""
    organization_id: NotRequired[str | None]
    """The ID of the organization that owns this project"""
    featured_gallery: NotRequired[str | None]
    """The featured gallery image of the project"""
    icon_color: NotRequired[int | None]
    """The RGB color of the project, automatically generated from the project icon"""
    client_side: DependencyTypes  # Deprecated, use environment. but my stuff don't really work with the new thing
    """Deprecated - use environment instead. The client side support of the project"""
    server_side: DependencyTypes  # Deprecared, use environment. but my stuff don't really work with the new thing
    """Deprecated - use environment instead. The server side support of the project"""


class SearchResult(TypedDict):
    project_hits: list[SearchHit]
    """The list of results"""
    result_offset: int
    """The number of results that were skipped by the query"""
    result_limit: int
    """The number of results that were returned by the query"""
    total_hits: int
    """The total number of results that match the query"""
