import zipapp
from pathlib import Path

source_dir = Path("mcserver")

target_dir = Path("dist")
target_file = target_dir / "mcserver"

target_dir.mkdir(exist_ok=True)

print("Zipping app...")
zipapp.create_archive(source_dir, target_file, "/usr/bin/env python3")
print("Done!")
