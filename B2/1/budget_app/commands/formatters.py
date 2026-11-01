import unicodedata
from collections.abc import Iterable
from ..models.budget import BudgetStatus
from ..models.transaction import Transaction


def display_width(text: str) -> int:
    """터미널 표시 폭 계산 — 한글 등 전각 문자는 2칸으로 셉니다."""
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def pad(text: str, width: int, align_right: bool = False) -> str:
    padding = " " * max(width - display_width(text), 0)
    return padding + text if align_right else text + padding


def format_table(header: list[str], rows: list[list[str]], right_align: set[int] = frozenset()) -> list[str]:
    """
    헤더 + 구분선 + 행을 컬럼 폭에 맞춰 정렬한 문자열 줄로 변환 (외부 라이브러리 없이).
    right_align의 컬럼(금액 등)은 오른쪽 정렬합니다.
    """
    if not rows:
        return []

    widths = [max(display_width(row[col]) for row in [header, *rows]) for col in range(len(header))]

    def render(row: list[str]) -> str:
        # 뒤쪽의 빈 컬럼(메모/태그 없음)은 구분자까지 생략
        last = len(row)
        while last > 0 and not row[last - 1]:
            last -= 1
        cells = [pad(row[col], widths[col], align_right=(col in right_align)) for col in range(last)]
        return " | ".join(cells).rstrip()

    separator = "-+-".join("-" * width for width in widths)
    return [render(header), separator, *(render(row) for row in rows)]


def format_transactions(transactions: Iterable[Transaction]) -> list[str]:
    header = ["id", "날짜", "타입", "카테고리", "금액", "메모", "태그"]
    rows = [
        [
            tx.id,
            tx.date.isoformat(),
            tx.type.value,
            tx.category,
            f"{tx.amount:,}",
            tx.memo,
            ",".join(f"#{tag}" for tag in tx.tags),
        ]
        for tx in transactions
    ]
    return format_table(header, rows, right_align={4})


def format_won(amount: int) -> str:
    return f"{amount:,}원"


def format_budget_status(status: BudgetStatus) -> list[str]:
    """예산 사용률 + 초과 경고 (summary, budget show 공용)"""
    lines = [f"예산: {format_won(status.budget)} (사용률 {status.usage_percent}%)"]
    if status.is_exceeded:
        lines.append(f"⚠️  [경고] 예산을 {format_won(-status.remaining)} 초과했습니다!")
    else:
        lines.append(f"남은 예산: {format_won(status.remaining)}")
    return lines
