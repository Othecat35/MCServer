def main():
    import sys
    MIN_PYTHON_VERSION: tuple[int, int] = (3, 14)
    if sys.version_info < MIN_PYTHON_VERSION:
        sys.exit(f"MCServer requires Python {'.'.join(map(str, MIN_PYTHON_VERSION))} or newer.")

    import os
    debug_mode = os.getenv("MCSERVER_DEBUG") == "1"

    import logging as log
    log_level = log.DEBUG if debug_mode else log.INFO
    log.basicConfig(level=log_level)

    from . import cli
    sys.exit(cli.main())
