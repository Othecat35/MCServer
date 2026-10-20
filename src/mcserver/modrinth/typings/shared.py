from typing import Literal

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

type EnvironmentSide = Literal["required", "optional", "unsupported", "unknown"]
type ProjectType = Literal["mod", "modpack", "resourcepack", "shader"]
