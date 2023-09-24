import functools
from pathlib import Path
from typing import Optional, Union

from dotenv import dotenv_values

from autoshop.util.logging import logger as get_logger


PATH_DOTENV_DEFAULT = Path(__file__).parents[2] / ".env"
LOGGER = get_logger(__name__)
TYPE_ENVIRONMENT_VALUE = Union[str, int, float]


@functools.lru_cache(maxsize=None)
def get_environment_variables(
    path: Optional[Path] = None,
) -> dict[str, TYPE_ENVIRONMENT_VALUE]:
    if path is None:
        path = PATH_DOTENV_DEFAULT
    LOGGER.info(f"Loading from environment variables from {path=}")
    return dotenv_values(dotenv_path=path)


def get(
    key: str,
    path: Optional[Path] = None,
) -> TYPE_ENVIRONMENT_VALUE:
    environment_variables = get_environment_variables(path=path)
    return environment_variables[key]
