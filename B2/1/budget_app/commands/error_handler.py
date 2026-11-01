import functools
import logging
import sys
from collections.abc import Callable
from typing import ParamSpec, TypeVar
from ..errors import (
    BudgetAppError,
    CategoryInUseError,
    CategoryNotFoundError,
    DuplicateCategoryError,
    InvalidCsvHeaderError,
    NothingToUpdateError,
    SameReplacementCategoryError,
    SourceFileNotFoundError,
    TransactionNotFoundError,
)

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger("budget_app")

DEFAULT_HINT = "'python -m budget_app <command> --help' 명령어로 올바른 사용법을 확인하세요."


class UsageError(BudgetAppError):
    """CLI 옵션 조합이 잘못됨 — CLI 계층에서만 쓰므로 해결 힌트를 직접 가짐"""

    def __init__(self, message: str, hint: str):
        super().__init__(message)
        self.hint = hint


def hint_for(error: BudgetAppError) -> str:
    """
    애플리케이션 예외에 CLI 사용법 안내를 붙입니다.
    UseCase는 명령어/옵션 이름을 모르고, 그 지식은 이 함수 한 곳에만 있습니다.
    """
    match error:
        case UsageError():
            return error.hint
        case TransactionNotFoundError():
            return "'python -m budget_app list'로 id를 확인하세요."
        case CategoryNotFoundError():
            return (f"'python -m budget_app category list'로 확인하거나, "
                    f"'python -m budget_app category add --name {error.name}'로 먼저 등록하세요.")
        case DuplicateCategoryError():
            return "'python -m budget_app category list'로 등록된 카테고리를 확인하세요."
        case CategoryInUseError():
            return "'--replace-with <카테고리>'로 대체 카테고리를 지정하면 거래를 옮긴 뒤 삭제합니다."
        case SameReplacementCategoryError():
            return "다른 카테고리를 --replace-with로 지정하세요."
        case NothingToUpdateError():
            return "--date, --type, --category, --amount, --memo, --tags 중 하나 이상을 지정하세요."
        case SourceFileNotFoundError():
            return "파일 경로를 확인하세요."
        case InvalidCsvHeaderError():
            return f"헤더에 {','.join(error.required)} 컬럼이 있어야 합니다 (선택: memo,tags / UTF-8)."
        case _:
            return DEFAULT_HINT


def handle_errors(func: Callable[P, R]) -> Callable[P, R]:
    """
    예외를 스택트레이스 대신 '[오류] 원인 + [힌트] 해결 방법'으로 출력하고
    0이 아닌 종료 코드로 프로그램을 끝냅니다.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            print("\n[취소] 사용자에 의해 작업이 취소되었습니다.", file=sys.stderr)
            sys.exit(130)
        except EOFError:
            _print_error("\n[오류] 입력이 중간에 종료되었습니다.",
                         "대화형 입력 항목을 모두 입력하거나, 옵션 인자로 값을 넘겨주세요.")
        except BudgetAppError as e:
            _print_error(f"[오류] {e}", hint_for(e))
        except ValueError as e:
            _print_error(f"[오류] {e}", DEFAULT_HINT)
        except OSError as e:
            _print_error(f"[오류] 파일을 처리할 수 없습니다: {e.filename or ''} ({e.strerror})",
                         "파일 경로와 권한, --data-dir 위치를 확인하세요.")
        except Exception as e:  # noqa: BLE001 — 최상단 진입점: 스택트레이스 대신 원인 + 힌트 출력
            logger.debug("예상하지 못한 오류", exc_info=True)
            _print_error(f"[오류] 예상하지 못한 오류가 발생했습니다: {e}",
                         "--verbose 옵션으로 다시 실행하면 상세 로그를 볼 수 있습니다.")

    return wrapper


def _print_error(message: str, hint: str) -> None:
    print(message, file=sys.stderr)
    print(f"[힌트] {hint}", file=sys.stderr)
    sys.exit(1)
