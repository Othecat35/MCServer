from pathlib import Path
import os

cache_dir = Path.home() / ".cache"

xdg_cache_dir = os.getenv("XDG_CACHE_DIR")
if xdg_cache_dir:
    cache_dir = Path(xdg_cache_dir)

mcserver_cache_dir = cache_dir / "mcserver"

def create_file(file_name: str, file_data: bytes):
    mcserver_cache_dir.mkdir(parents=True, exist_ok=True)
    cache_file = mcserver_cache_dir / file_name
    cache_file.write_bytes(file_data)