import os
from pathlib import Path

home_dir = Path.home()
working_dir = Path.cwd()

mcserver_dir = working_dir / ".mcserver"
metadata_file = mcserver_dir / "metadata.json"
configs_dir = mcserver_dir / "configs"

mods_dir = working_dir / "mods"
plugins_dir = working_dir / "plugins"

cache_dir = Path.home() / ".cache"
xdg_cache_dir = os.getenv("XDG_CACHE_HOME")
if xdg_cache_dir:
    cache_dir = Path(xdg_cache_dir)

mcserver_cache_dir = cache_dir / "mcserver"
