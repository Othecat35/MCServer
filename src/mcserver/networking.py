# Modules
# Standard
import hashlib
import json
import logging
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import TypedDict

# MCServer
from . import __version__
from .shared import (
    current_dir,
    format_number,
    mcserver_dir,
    pluralize,
    print_status,
    print_string,
)

logger = logging.getLogger(__name__)


# TypedDict
class ResponseObject(TypedDict):
    text: str
    json: dict | list | None
    headers: dict
    status_code: int


# Errors
class DownloadURLError(Exception):
    pass


# Variables
user_agent = (
    f"MCServer/{__version__} (Othecat35; +https://github.com/Othecat35/MCServer)"
)
read_chunk_size: int = 1024 * 64  # 64KiB

# Paths
tempfiles_dir = mcserver_dir / "tempfiles"


# Functions
def request(
    url: str,
    query: dict | None = None,
    data: bytes | None = None,
    headers: dict | None = None,
    method: str = "GET",
    timeout: int = 10,
    always_json: bool = False
) -> ResponseObject:
    method = method.upper()
    if query is None:
        query = {}
    if headers is None:
        headers = {}
    headers.setdefault("User-Agent", user_agent)

    query_string = f"?{urllib.parse.urlencode(query)}" if query else ""
    request = urllib.request.Request(
        f"{url}{query_string}", data=data, headers=headers, method=method
    )

    logger.debug(f"Requesting URL: {method} {request.full_url}")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            logger.debug(f"Responded with status: {response.status} {response.reason}")

            response_headers = {}
            for key, value in response.getheaders():
                response_headers[key.lower()] = value

            response_object: ResponseObject = {
                "status_code": response.code,
                "headers": response_headers,
                "text": response.read().decode("utf-8"),
                "json": None
            }

            if always_json or response_headers.get("content-type", "").startswith("application/json"):
                response_object["json"] = json.loads(response_object["text"])

            return response_object

    except urllib.error.HTTPError as response:
        response_headers = {}
        for key, value in response.getheaders():
            response_headers[key.lower()] = value

        response_object: ResponseObject = {
            "status_code": response.code,
            "headers": response_headers,
            "text": response.reason,
            "json": None
        }

        return response_object


def download(
    url: str,
    filename: str | Path,
    hashes: dict | None = None,
    headers: dict | None = None,
    timeout: int = 10,
    update_interval: int = 1,
) -> None:
    filename = Path(filename)
    if hashes is None:
        hashes = {}
    if headers is None:
        headers = {}
    headers.setdefault("User-Agent", user_agent)

    basename = filename.name
    tempfile = tempfiles_dir / basename

    request_url = urllib.request.Request(url, headers=headers, method="GET")

    logger.debug(f"Downloading URL: {request_url.full_url}")
    logger.debug(f"Temporary file: {tempfile}")

    hash_algorithm = None
    hash_name = None

    if hashes.get("sha512"):
        hash_algorithm = hashlib.sha512()
        hash_name = "sha512"
    elif hashes.get("sha256"):
        hash_algorithm = hashlib.sha256()
        hash_name = "sha256"
    elif hashes.get("sha1"):
        hash_algorithm = hashlib.sha1()
        hash_name = "sha1"
    elif hashes.get("md5"):
        hash_algorithm = hashlib.md5(usedforsecurity=False)
        hash_name = "md5"

    expected_hash = None

    if hash_name:
        expected_hash = hashes[hash_name]
        logger.debug(f"Calculating hash {hash_name} while downloading...")
        logger.debug(f"Expected {hash_name}: {expected_hash}")

    with urllib.request.urlopen(request_url, timeout=timeout) as response:
        content_length = int(response.getheader("Content-Length", default=0))
        downloaded_length = 0
        start_time: float = time.monotonic()
        last_updated: float = start_time
        last_updated_time: float = start_time
        last_updated_length: int = 0

        with open(tempfile, mode="wb") as file:
            while True:
                data = response.read(read_chunk_size)

                if not data:
                    break

                if hash_algorithm:
                    hash_algorithm.update(data)

                file.write(data)
                downloaded_length += len(data)

                time_now: float = time.monotonic()
                if time_now - last_updated >= update_interval:
                    time_elapsed = time_now - last_updated_time
                    downloaded_bytes = downloaded_length - last_updated_length

                    download_rate = downloaded_bytes / time_elapsed if time_elapsed > 0 else 0
                    if content_length != 0:
                        print_status(
                            f"Downloading '{basename}' ({format_number(content_length, 'iec')})...",
                            updating_status=f"Downloading '{basename}' ({format_number(downloaded_length, 'iec')}/{format_number(content_length, 'iec')} {format_number(download_rate, "iec")}/s)... ({round(downloaded_length / content_length * 100)}%)",
                        )
                    else:
                        print_status(
                            f"Downloading '{basename}' (unknown final size)...",
                            updating_status=f"Downloading '{basename}' ({format_number(downloaded_length, 'iec')} {format_number(download_rate, "iec")}/s)...",
                        )

                    last_updated_length = downloaded_length
                    last_updated_time = time_now
                    last_updated = time_now

        if hash_algorithm:
            calculated_hash = hash_algorithm.hexdigest()

            logger.debug(f"Got hash: {calculated_hash}")
            if calculated_hash != expected_hash:
                raise DownloadURLError(
                    f"Downloaded file '{tempfile.relative_to(current_dir)}' hash does not match with the expected {hash_name} hash"
                )

        time_elapsed = round(time.monotonic() - start_time)
        print_string(f"Downloaded '{basename}' with size {format_number(downloaded_length, 'iec')} for {time_elapsed} {pluralize("second", time_elapsed)}")

    shutil.move(tempfile, filename)
