from typing import Literal, NotRequired, TypedDict
from .shared import Environment, EnvironmentSide, ProjectType

type AllProjectType = Literal[
    "mod", "resourcepack", "datapack", "shader", "modpack", "plugin"
]
type DisclosureType = Literal[
    "ai_content",
    "ai_content_code",
    "ai_content_assets",
    "ai_content_text",
    "ai_functionality",
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


class SearchHit(TypedDict):
    project_id: str
    """The ID of the project, encoded as a base62 string"""
    project_type: ProjectType
    """The project type of the project"""
    all_project_types: list[AllProjectType]
    """All project types across every version of the project, unlike project_type which only reflects a version-specific type"""
    project_name: str
    """The title or name of the project"""
    short_description: str
    """A short sentence summarizing the project, no more than a sentence or two."""
    author_username: str
    """The username of the project's author"""
    categories: list[str]
    """A list of the featured categories that the project has."""
    display_categories: list[str]
    """A list of the featured categories that the project has. Equivalent to categories on the project itself."""
    game_versions: list[str]
    """A list of the minecraft versions supported by the project"""
    download_count: int
    """The total number of downloads of the project"""
    follower_count: int
    """The total number of users following the project"""
    icon_url: str
    """The URL of the project's icon"""
    created_time: str
    """The date the project was created (format: ISO-8601)"""
    updated_time: str
    """The date the latest version of the project was created (format: ISO-8601)"""
    latest_version_id: str
    """The ID of the latest version of the project"""
    license_id: str
    """The SPDX license ID of a project"""
    environments: list[Environment]
    """All the environments that versions of this project support. Not in any particular order, we recommend using the environment information on a version instead. For an explanation of each environment, see the blog post here: https://modrinth.com/news/article/new-environments/#new-system"""
    disclosure_types: list[DisclosureType]
    """Disclosures listed on the project."""
    image_urls: list[str]
    """A list of images that have been uploaded to the project's gallery"""
    project_slug: NotRequired[str | None]
    """The slug of a project, used for vanity URLs."""
    author_id: NotRequired[str | None]
    """The ID of the project's author"""
    organization_name: NotRequired[str | None]
    """The name of the organization that owns this project"""
    organization_id: NotRequired[str | None]
    """The ID of the organization that owns this project"""
    featured_gallery: NotRequired[
        str | None
    ]  # What does this means? an URL? I haven't tested it yet
    """The featured gallery image of the project"""
    icon_color: NotRequired[int | None]
    """The RGB color of the project, automatically generated from the project icon"""
    client_side: EnvironmentSide
    """Deprecated - use environment instead. The client side support of the project"""
    server_side: EnvironmentSide
    """Deprecated - use environment instead. The server side support of the project"""


class SearchResult(TypedDict):
    search_hits: list[SearchHit]
    """The list of results"""
    result_offset: int
    """The number of results that were skipped by the query"""
    result_limit: int
    """The number of results that were returned by the query"""
    total_hits: int
    """The total number of results that match the query"""
