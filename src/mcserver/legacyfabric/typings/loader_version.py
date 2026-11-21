from .shared import Version


class LoaderVersion(Version):
    version_separator: str
    build_number: int
    maven_coordinate: str
