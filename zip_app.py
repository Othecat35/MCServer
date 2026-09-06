# Imports
import zipapp
from pathlib import Path

# Excluded Path
excluded_directories = "__pycache__"

# Paths
source_dir = Path("src/")

target_dir = Path("dist")
target_dir.mkdir(exist_ok=True)
target_file = target_dir / "mcserver.zip"

python_interpreter = "/usr/bin/env python3"

# Print Information
print(f"""\
Source      : '{source_dir}'
Interpreter : '{python_interpreter}'
Target      : '{target_file}'
""")


# Filter function
def filter_directories(file_path: Path) -> bool:
    if excluded_directories in file_path.parts:
        print(f"Excluding path : '{source_dir / file_path}'")
        return False

    return True


# Zip the App
print("Creating archive...")
zipapp.create_archive(
    source=source_dir,
    target=target_file,
    interpreter=python_interpreter,
    filter=filter_directories,
)
print("Zipping complete.")
