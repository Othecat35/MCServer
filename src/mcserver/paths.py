import os
from pathlib import Path

# user
home_dir: Path = Path.home()
current_dir: Path = Path.cwd()
working_dir: Path = Path.cwd()

# cache
cache_dir: Path = home_dir / ".cache"
xdg_cache_dir: str | None = os.getenv("XDG_CACHE_HOME")
if xdg_cache_dir is not None:
    cache_dir: Path = Path(xdg_cache_dir)

mcserver_cache_dir: Path = cache_dir / "mcserver"

slug_index_file = mcserver_cache_dir / "slug_index.json"

# system
proc_dir: Path = Path("/proc")

# .mcserver
mcserver_dir: Path = working_dir / ".mcserver"

configs_dir: Path = mcserver_dir / "configs"
tempfiles_dir = mcserver_dir / "tempfiles"

metadata_file: Path = mcserver_dir / "metadata.json"
state_file: Path = mcserver_dir / "state.json"

# modrinth
modrinth_dir: Path = mcserver_dir / "modrinth"
project_records_dir: Path = modrinth_dir / "project_records"

# project
mods_dir: Path = working_dir / "mods"
plugins_dir: Path = working_dir / "plugins"

# server
banned_ips_file = working_dir / "banned_ips.json"
banned_players_file = working_dir / "banned_players.json"

ops_file = working_dir / "ops.json"
server_properties_file = working_dir / "server.properties"
whitelist_file = working_dir / "whitelist.json"


# update working dir
def update_working_dir(path: Path = current_dir) -> None:
    global working_dir
    global mcserver_dir
    global configs_dir, tempfiles_dir
    global metadata_file, state_file
    global modrinth_dir, project_records_dir
    global mods_dir, plugins_dir
    global banned_ips_file, banned_players_file
    global ops_file, server_properties_file, whitelist_file

    working_dir = path.resolve()

    mcserver_dir = working_dir / ".mcserver"

    configs_dir = mcserver_dir / "configs"
    tempfiles_dir = mcserver_dir / "tempfiles"

    metadata_file = mcserver_dir / "metadata.json"
    state_file = mcserver_dir / "state.json"

    modrinth_dir = mcserver_dir / "modrinth"
    project_records_dir = modrinth_dir / "project_records"

    mods_dir = working_dir / "mods"
    plugins_dir = working_dir / "plugins"

    banned_ips_file = working_dir / "banned_ips.json"
    banned_players_file = working_dir / "banned_players.json"

    ops_file = working_dir / "ops.json"
    server_properties_file = working_dir / "server.properties"
    whitelist_file = working_dir / "whitelist.json"
