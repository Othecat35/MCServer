import zipapp
from pathlib import Path

source_dir = Path("mcserver/")
print(f"- Source      : '{source_dir}'")

target_dir = Path("dist")
target_dir.mkdir(exist_ok=True)

target_file = target_dir / "mcserver"
print(f"- Target      : '{target_file}'")

python_interpreter = "/usr/bin/env python3"
print(f"- Interpreter : '{python_interpreter}'")

print("Creating archive...")
zipapp.create_archive(source=source_dir, target=target_file, interpreter=python_interpreter)
print("Done!")
