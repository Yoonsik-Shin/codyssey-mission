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


def format_transactions(transactions: Iterable[Transaction]) -> list[str]:
    """거래 목록을 컬럼 폭을 맞춘 테이블 문자열 줄로 변환 (외부 라이브러리 없이 정렬)"""
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
    if not rows:
        return []

    widths = [max(display_width(row[col]) for row in rows) for col in range(len(rows[0]))]
    amount_col = 4

    lines = []
    for row in rows:
        # 뒤쪽의 빈 컬럼(메모/태그 없음)은 구분자까지 생략
        last = len(row)
        while last > 0 and not row[last - 1]:
            last -= 1
        cells = [pad(row[col], widths[col], align_right=(col == amount_col)) for col in range(last)]
        lines.append(" | ".join(cells).rstrip())
    return lines


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
