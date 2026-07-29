def main() -> None:
    import sys

    if ((sys.argv[1] if len(sys.argv) > 1 else "") == "cake"):
        from .mysterious import nothing_to_see_here_move_along
        nothing_to_see_here_move_along()

    MIN_PYTHON_VERSION: tuple[int, int] = (3, 14)
    if sys.version_info < MIN_PYTHON_VERSION:
        sys.exit(f"MCServer requires Python {'.'.join(map(str, MIN_PYTHON_VERSION))} or newer.")

    import os
    import logging as log
    from . import cli

    debug_mode = os.getenv("MCSERVER_DEBUG") == "1"
    log_level = log.DEBUG if debug_mode else log.INFO
    log.basicConfig(level=log_level, format="[%(levelname)s]: %(message)s")

    sys.exit(cli.main())
