import os
from pathlib import Path

# user
home_dir: Path = Path.home()
current_dir: Path = Path.cwd()
working_dir: Path = Path.cwd()

# .mcserver
mcserver_dir: Path = working_dir / ".mcserver"

metadata_file: Path = mcserver_dir / "metadata.json"
state_file: Path = mcserver_dir / "state.json"

configs_dir: Path = mcserver_dir / "configs"
tempfiles_dir = mcserver_dir / "tempfiles"

# modrinth
modrinth_dir: Path = mcserver_dir / "modrinth"
project_records_dir: Path = modrinth_dir / "project_records"

# project
mods_dir: Path = working_dir / "mods"
plugins_dir: Path = working_dir / "plugins"

# cache
cache_dir: Path = home_dir / ".cache"
xdg_cache_dir: str | None = os.getenv("XDG_CACHE_HOME")
if xdg_cache_dir is not None:
    cache_dir: Path = Path(xdg_cache_dir)

mcserver_cache_dir: Path = cache_dir / "mcserver"

# system
proc_dir: Path = Path("/proc")

def update_working_dir(path: Path) -> None:
    global working_dir
    global mods_dir, plugins_dir
    working_dir = path

    mods_dir = path / "mods"
    plugins_dir = path / "plugins"