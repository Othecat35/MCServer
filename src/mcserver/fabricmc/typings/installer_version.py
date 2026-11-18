from typing import TypedDict


class InstallerVersion(TypedDict):
    download_url: str
    maven_coordinate: str
    version_string: str
    is_stable: bool
