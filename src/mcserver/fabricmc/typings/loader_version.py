from typing import TypedDict


class LoaderVersion(TypedDict):
    version_separator: str
    build_number: int
    maven_coordinate: str
    version_string: str
    is_stable: bool
