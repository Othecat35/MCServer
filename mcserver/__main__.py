import sys
if sys.version_info < (3, 12):
  print("MCServer requires Python 3.12 or newer.")
  sys.exit(1)

from cli import main
main()
