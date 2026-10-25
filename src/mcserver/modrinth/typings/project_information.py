from typing import Literal, NotRequired, TypedDict

from .shared import Environment, EnvironmentSide, ProjectType

type MonetizationStatus = Literal["monetized", "demonetized", "force-demonetized"]
type ProjectStatus = Literal[
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
type RequestedProjectStatus = Literal["approved", "archived", "unlisted", "private", "draft"]


class ProjectLicense(TypedDict):
    license_id: NotRequired[str]
    """The SPDX license ID of a project"""
    license_name: NotRequired[str]
    """The long name of a license"""
    license_url: NotRequired[str | None]
    """The URL to this license"""


class GalleryImage(TypedDict):
    image_url: str
    """The URL of the gallery image"""
    is_featured: bool
    """Whether the image is featured in the gallery"""
    image_title: NotRequired[str | None]
    """The title of the gallery image"""
    image_description: NotRequired[str | None]
    """The description of the gallery image"""
    created_time: str
    """The date and time the gallery image was created (format: ISO-8601)"""
    ordering_number: NotRequired[int]
    """The order of the gallery image. Gallery images are sorted by this field and then alphabetically by title."""


class DonationPlatform(TypedDict):
    platform_id: NotRequired[str]
    """The ID of the donation platform"""
    platform_name: NotRequired[str]
    """The donation platform this link is to"""
    donation_url: NotRequired[str]
    """The URL of the donation platform and user"""


class ModeratorMessage(TypedDict):
    message: NotRequired[str]
    """The message that a moderator has left for the project"""
    body: NotRequired[str | None]
    """The longer body of the message that a moderator has left for the project"""


class ProjectInformation(TypedDict):
    project_id: str
    """The ID of the project, encoded as a base62 string"""
    team_id: str
    """The ID of the team that has ownership of this project"""
    project_name: str
    """The title or name of the project"""
    short_description: str
    """A short sentence summarizing the project, no more than a sentence or two."""
    description: str
    """A long form description of the project"""
    project_status: ProjectStatus
    """The status of the project"""
    project_type: ProjectType
    """The project type of the project"""
    categories: list[str]
    """A list of the featured categories that the project has."""
    additional_categories: list[str]
    """A list of additional categories that the project also has. These are supplementary to the featured categories, and does not include them again."""
    environments: list[Environment]
    """All the environments that versions of this project support. Not in any particular order, we recommend using the environment information on a version instead. For an explanation of each environment, see the blog post here: https://modrinth.com/news/article/new-environments/#new-system"""
    game_versions: list[str]
    """A list of all of the game versions supported by the project"""
    loader_names: list[str]
    """A list of all of the loaders supported by the project. These vary based on project type."""
    version_ids: list[str]
    """A list of the version IDs of the project"""
    project_license: ProjectLicense
    """The license of the project"""
    published_time: str
    """The date the project was created (format: ISO-8601)"""
    updated_time: str
    """The date the latest version of the project was created (format: ISO-8601)"""
    download_count: int
    """The total number of downloads of the project"""
    follower_count: int
    """The total number of users following the project"""
    gallery: list[GalleryImage]
    """A list of images that have been uploaded to the project's gallery"""
    thread_id: str
    """The ID of the moderation thread associated with this project"""
    monetization_status: MonetizationStatus
    """No description from Modrinth ;-;"""
    project_slug: NotRequired[str | None]
    """The slug of a project, used for vanity URLs."""
    organization_id: NotRequired[str | None]
    """The ID of the organization that owns this project"""
    requested_project_status: NotRequired[RequestedProjectStatus | None]
    """The requested status when submitting for review or scheduling the project for release. Approved status refers to “Public” visibility."""
    approved_time: NotRequired[str | None]
    """The date the project was first published (format: ISO-8601)"""
    queued_time: NotRequired[str | None]
    """The date the project's status was submitted to moderators for review (format: ISO-8601)"""
    icon_url: NotRequired[str | None]
    """The URL of the project's icon"""
    raw_icon_url: NotRequired[str | None]
    """The URL of the project's icon without CDN transforms applied"""
    icon_color: NotRequired[int | None]
    """The RGB color of the project, automatically generated from the project icon"""
    issues_url: NotRequired[str | None]
    """An optional link to where to submit bugs or issues with the project"""
    source_url: NotRequired[str | None]
    """An optional link to the source code of the project"""
    wiki_url: NotRequired[str | None]
    """An optional link to the project's wiki page or other relevant information"""
    discord_url: NotRequired[str | None]
    """An optional invite link to the project's discord"""
    donation_platforms: NotRequired[list[DonationPlatform] | None]
    """A list of donation links for the project"""
    client_side: EnvironmentSide
    """Deprecated - use environment instead."""
    server_side: EnvironmentSide
    """Deprecated - use environment instead."""
    body_url: NotRequired[str | None]
    """Deprecated - The link to the long description of the project. Always null, only kept for legacy compatibility."""
    moderator_message: NotRequired[ModeratorMessage]
    """Deprecated - A message that a moderator sent regarding the project"""
