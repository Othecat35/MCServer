import os
from pathlib import Path

home_dir = Path.home()
current_dir = Path.cwd()

mcserver_dir = current_dir / ".mcserver"
configs_dir = mcserver_dir / "configs"

mods_dir = current_dir / "mods"
plugins_dir = current_dir / "plugins"

cache_dir = Path.home() / ".cache"
xdg_cache_dir = os.getenv("XDG_CACHE_DIR")
if xdg_cache_dir:
    cache_dir = Path(xdg_cache_dir)

mcserver_cache_dir = cache_dir / "mcserver"
