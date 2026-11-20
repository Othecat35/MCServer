from typing import Literal, TypedDict

type BuildChannel = Literal["ALPHA", "BETA", "STABLE", "RECOMMENDED"]

class FileHashes(TypedDict):
    sha256: str

class BuildDownload(TypedDict):
    file_name: str
    file_hashes: FileHashes
    file_size: int
    download_url: str

class BuildCommit(TypedDict):
    commit_hash: str
    commit_time: str
    commit_message: str

class BuildInformation(TypedDict):
    build_id: int
    build_time: str
    build_channel: BuildChannel
    build_commits: list[BuildCommit]
    build_downloads: dict[str, BuildDownload]
