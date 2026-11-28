import logging
from argparse import Namespace

from .. import paths

logger: logging.Logger = logging.getLogger(__name__)

def remove_projects(args: Namespace) -> int:
    paths.update_working_dir(args.directory)
    logger.error("Command is not implemented yet.")
    return 1
