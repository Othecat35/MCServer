#Modules
# Standard
import json, zipfile

from pathlib import Path
from typing import Literal, NotRequired, TypedDict

#TYpedDict
class FileHashes(TypedDict):
    sha1: str     #original: sha1
    sha512: str #original: sha512

class ModEnvironment(TypedDict):
    client_side: Literal["required", "optional", "unsupported", "unknown"] #original: client
    server_side: Literal["required", "optional", "unsupported", "unknown"] #original: server

class File(TypedDict):
    file_path: Path                                                            #original: path
    hashes: FileHashes                                                     #original: hashes
    mod_environment: NotRequired[ModEnvironment] #original: env
    download_urls: list[str]                                         #original: downloads
    file_size: int                                                             #original: fileSize

class ModPackIndex(TypedDict):
    format_version: int                         #original: formatVersion
    game_name: Literal["minecraft"] #original: game
    version_id: str                                 #original: versionId
    pack_name: str                                    #original: name
    pack_summary: NotRequired[str]    #original: summary
    files: list[File]                             #original: files
    dependencies: dict[str, str]        #original: dependencies

#Functions
def read_index(file_path: Path | str) -> ModPackIndex:
    file_path = Path(file_path)

    pack_index = {}
    with zipfile.ZipFile(file_path) as zip_file:
        pack_index = json.loads(zip_file.read("modrinth.index.json").decode())

    files = []
    for file in pack_index["files"]:
        files.append({
            "file_path": Path(file["path"]),
            "hashes": file["hashes"],
            "mod_environment": file.get("env"),
            "download_urls": file["downloads"],
            "file_size": file["fileSize"]
        })

    return {
        "format_version": pack_index["formatVersion"],
        "game_name": pack_index["game"],
        "version_id": pack_index["versionId"],
        "pack_name": pack_index["name"],
        "pack_summary": pack_index.get("summary"),
        "files": files,
        "dependencies": pack_index["dependencies"]
    }

def _extract_zip(zip_file: zipfile.ZipFile, zip_path: str, path: Path | str = Path.cwd()):
    path = Path(path)
    for entry in zip_file.namelist():
        if not entry.startswith(zip_path):
            continue

        destination_path = path / entry.removeprefix(zip_path)
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        if entry.endswith("/"):
            destination_path.mkdir(exist_ok=True)
        else:
            destination_path.write_bytes(zip_file.read(entry))

def apply_overrides(file_path: str | Path) -> None:
    file_path = Path(file_path)

    with zipfile.ZipFile(file_path) as zip_file:
        _extract_zip(zip_file, "overrides/")

def apply_server_overrides(file_path: str | Path) -> None:
    file_path = Path(file_path)

    with zipfile.ZipFile(file_path) as zip_file:
        _extract_zip(zip_file, "server-overrides/")
