import logging

from .shared import ansi


# Log handler
class ClearLineHandler(logging.StreamHandler):
    def emit(self, record):
        self.stream.write(ansi("clear_line") + ansi("start_line"))
        self.stream.flush()
        super().emit(record)


def main():
    import sys

    MIN_PYTHON_VERSION: tuple[int, int] = (3, 12)
    if sys.version_info < MIN_PYTHON_VERSION:
        sys.exit(
            f"MCServer requires Python {'.'.join(map(str, MIN_PYTHON_VERSION))} or newer."
        )

    if (sys.argv[1] if len(sys.argv) > 1 else "") == "uh...":
        from .mysterious import nothing_to_see_here_move_along

        nothing_to_see_here_move_along()

    import os

    from . import cli

    debug_mode = os.getenv("MCSERVER_DEBUG") == "1"
    if debug_mode:
        logging.basicConfig(
            level=logging.DEBUG, format="[%(levelname)s] [%(module)s]: %(message)s"
        )
    else:
        logging.basicConfig(level=logging.INFO, format="[%(levelname)s]: %(message)s")

    sys.exit(cli.main())
