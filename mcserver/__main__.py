import sys
if sys.version_info < (3, 13):
  print("MCServer requires Python 3.13 or newer.")
  sys.exit(1)

from cli import main
main()
