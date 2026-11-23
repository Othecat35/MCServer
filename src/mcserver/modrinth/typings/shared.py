from typing import Literal, NotRequired, TypedDict

type DependencyType = Literal["required", "optional", "incompatible", "embedded"]
type EnvironmentSide = Literal["required", "optional", "unsupported", "unknown"]
type ProjectType = Literal["mod", "modpack", "resourcepack", "shader"]


class Dependency(TypedDict):
    project_id: NotRequired[str | None]
    """The ID of the project that this version depends on"""
    dependency_type: DependencyType
    """The type of dependency that this version has"""


type Environment = Literal[
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
