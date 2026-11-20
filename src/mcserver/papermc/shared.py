from typing import get_args

from .typings import BuildChannel

BUILD_CHANNEL: frozenset[str] = frozenset(get_args(BuildChannel.__value__))
