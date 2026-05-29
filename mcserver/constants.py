from pathlib import Path

__version__: str = "1.13.11"

current_dir: Path = Path.cwd()
mcserver_dir: Path = Path(".mcserver")

modrinth_api_base: str = "https://api.modrinth.com/v2/"

si_prefixes = ["", "K", "M", "B", "T"]
iec_prefixes = ["B", "KiB", "MiB", "GiB", "TiB"]