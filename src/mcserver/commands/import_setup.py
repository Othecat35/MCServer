import logging
from argparse import Namespace

from .. import paths

logger: logging.Logger = logging.getLogger(__name__)


def import_setup(args: Namespace) -> int:
    paths.update_working_dir(args.directory)
    file: str = args.file

    logger.error("Command is not implemented yet.")
    return 1
