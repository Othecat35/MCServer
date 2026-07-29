# Imports
import zipapp
from pathlib import Path

# Paths
source_dir = Path("src/")

target_dir = Path("dist")
target_dir.mkdir(exist_ok=True)
target_file = target_dir / "mcserver"

python_interpreter = "/usr/bin/env python3"

# Print Information
print(f"""\
Source      : '{source_dir}'
Interpreter : '{python_interpreter}'
Target      : '{target_file}'
""")

# Filter function
def filter_file(file: Path) -> bool:
    if file.name in ["__pycache__"]:
        print(f"Ignoring path: '{source_dir}/{file}'")
        return False

    return True

# Zip the App
print("Creating archive...")
zipapp.create_archive(source=source_dir, target=target_file, interpreter=python_interpreter, filter=filter_file)
print("Zipping complete.")
