import sys

min_python_version = (3, 14)
if sys.version_info < min_python_version:
    print(f"MCServer requires Python {'.'.join(map(str, min_python_version))} or newer.")
    sys.exit(1)

from cli import main
main()
