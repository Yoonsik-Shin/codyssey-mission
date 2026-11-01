import functools
import logging
import time
from collections.abc import Callable
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger("budget_app")


def log_execution(func: Callable[P, R]) -> Callable[P, R]:
    """함수 실행 시작/종료와 소요 시간을 로그로 남깁니다 (--verbose 시 출력)."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.info("%s 시작", func.__qualname__)
        started = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - started
            logger.info("%s 종료 (%.3fs)", func.__qualname__, elapsed)

    return wrapper
