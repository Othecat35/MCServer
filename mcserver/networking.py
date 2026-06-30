#Modules
# Standard
import hashlib, shutil

import urllib.parse, urllib.request
import logging as log

from pathlib import Path
from typing import  TypedDict

# MCServer
from constants import __version__
from shared import current_dir, format_number, mcserver_dir, print_status

#TypedDict
class ResponseObject(TypedDict):
  body: str
  headers: dict
  status: int

#Errors
class DownloadURLError(Exception): pass

#Variables
user_agent = f"Othecat35/MCServer/{__version__} (https://github.com/Othecat35/MCServer)"
read_chunk_size: int = 1024 * 64 # 64KiB

#Paths
tempfiles_dir = mcserver_dir / "tempfiles"

#Functions
def request(url: str, query: dict | None = None, data: dict | None = None, headers: dict | None = None, method: str = "GET", timeout: int = 10) -> ResponseObject:
  method = method.upper()
  if query is None: query = {}
  if headers is None: headers = {}
  headers.setdefault("User-Agent", user_agent)

  query_string = f"?{urllib.parse.urlencode(query)}" if query else ""
  request = urllib.request.Request(f"{url}{query_string}", data=data, headers=headers, method=method)

  log.debug(f"Requesting URL: {method} {request.full_url}")
  with urllib.request.urlopen(request, timeout=timeout) as response:
    log.debug(f"Responded with status: {response.status} {response.reason}")

    response_headers = {}
    for key, value in response.getheaders():
      response_headers[key.lower()] = value

    return {
      "body": response.read().decode("utf-8"),
      "headers": response_headers,
      "status": response.status
    }

def download(url: str, filename: str | Path, hashes: dict | None | None = None, headers: dict | None = None, timeout: int = 10):
  filename = Path(filename)
  if hashes is None: hashes = {}
  if headers is None: headers = {}
  headers.setdefault("User-Agent", user_agent)

  basename = filename.name
  tempfile = tempfiles_dir / basename

  request_url = urllib.request.Request(url, headers=headers, method="GET")

  log.debug(f"Downloading URL: {request_url.full_url}")
  log.debug(f"Temporary file: {tempfile}")

  hash_algorithm = None
  hash_name = None

  if hashes.get("sha512"):
    hash_algorithm = hashlib.sha512()
    hash_name = "sha512"
  elif hashes.get("sha1"):
    hash_algorithm = hashlib.sha1()
    hash_name = "sha1"

  expected_hash = None

  if hash_name:
    expected_hash = hashes[hash_name]
    log.debug(f"Calculating hash {hash_name} while downloading...")
    log.debug(f"Expected {hash_name}: {expected_hash}")

  with urllib.request.urlopen(request_url, timeout=timeout) as response:
    content_length = int(response.getheader("Content-Length", default=0))
    downloaded_length = 0

    with open(tempfile, mode="wb") as file:
      while True:
        data = response.read(read_chunk_size)

        if not data:
          break

        if hash_algorithm:
          hash_algorithm.update(data)

        downloaded_length += len(data)

        if content_length == 0:
          print_status(f"Downloading {basename}... (unknown final size)", dynamic=f"Downloading {basename}... {format_number(downloaded_length, 'iec')}")
        else:
          print_status(f"Downloading {basename}... File size: {format_number(content_length, 'iec')}", dynamic=f"Downloading {basename}... {format_number(downloaded_length, 'iec')}/{format_number(content_length, 'iec')} ({round(downloaded_length / content_length * 100)}%)")

        file.write(data)

    if hash_algorithm:
      calculated_hash = hash_algorithm.hexdigest()

      log.debug(f"Got hash: {calculated_hash}")
      if calculated_hash != expected_hash:
        raise DownloadURLError(f"Downloaded file '{tempfile.relative_to(current_dir)}' hash does not match with the expected {hash_name} hash")

  shutil.move(tempfile, filename)
