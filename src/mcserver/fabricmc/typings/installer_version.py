from .shared import Version


class InstallerVersion(Version):
    download_url: str
    maven_coordinate: str
    version_string: str
