from .shared import Version


class LoaderVersion(Version):
    build_number: int
    """The build number of the loader"""
    version_separator: str
    """The separator used in the loader version"""
