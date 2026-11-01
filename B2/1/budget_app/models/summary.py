from collections.abc import Iterable
from dataclasses import dataclass, field
from .period import Month
from .transaction import Transaction, TransactionType


@dataclass
class MonthlySummary:
    """월별 수입/지출 집계 결과 (값 객체)"""
    month: Month
    total_income: int = 0
    total_expense: int = 0
    expense_by_category: dict[str, int] = field(default_factory=dict)
    count: int = 0

    @classmethod
    def from_transactions(cls, month: Month, transactions: Iterable[Transaction]) -> "MonthlySummary":
        """
        거래를 한 건씩 순회하며 해당 월만 집계합니다.
        제너레이터를 넘기면 거래 전체를 메모리에 올리지 않고 합계만 유지합니다.
        """
        summary = cls(month=month)
        for tx in transactions:
            if Month.of(tx.date) != month:
                continue

            summary.count += 1
            if tx.type == TransactionType.INCOME:
                summary.total_income += tx.amount
            else:
                summary.total_expense += tx.amount
                summary.expense_by_category[tx.category] = (
                    summary.expense_by_category.get(tx.category, 0) + tx.amount
                )
        return summary

    @property
    def balance(self) -> int:
        return self.total_income - self.total_expense

    @property
    def is_empty(self) -> bool:
        return self.count == 0

    def top_expense_categories(self, n: int) -> list[tuple[str, int]]:
        """지출 합계가 큰 순서로 카테고리 TOP N (금액이 같으면 이름순)"""
        ranked = sorted(self.expense_by_category.items(), key=lambda item: (-item[1], item[0]))
        return ranked[:n]
