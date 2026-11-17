from typing import TypedDict


class Hashes(TypedDict):
    sha1: str
    """The SHA-1 hash"""
    sha256: str
    """The SHA-256 hash"""
    sha512: str
    """The SHA-512 hash"""
