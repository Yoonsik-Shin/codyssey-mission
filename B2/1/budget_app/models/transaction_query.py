from dataclasses import dataclass
from datetime import date
from .category import Category
from .period import Month
from .transaction import Transaction, TransactionType


@dataclass(frozen=True)
class TransactionQuery:
    """
    거래 검색 조건 (값 객체).
    모든 조건은 AND로 결합되며, None인 조건은 검사하지 않습니다.
    """
    date_from: date | None = None
    date_to: date | None = None
    category: str | None = None
    type: TransactionType | None = None
    keyword: str | None = None   # 메모 부분 일치 (대소문자 무시)
    tag: str | None = None       # 태그 정확히 일치 (대소문자 무시)

    def __post_init__(self):
        if self.date_from is not None and self.date_to is not None and self.date_from > self.date_to:
            raise ValueError(f"시작일이 종료일보다 늦습니다: {self.date_from} > {self.date_to}")

    @classmethod
    def for_month(cls, month: Month) -> "TransactionQuery":
        """해당 월 1일 ~ 말일 기간 조건"""
        return cls(date_from=month.first_day, date_to=month.last_day)

    def matches(self, tx: Transaction) -> bool:
        if self.date_from is not None and tx.date < self.date_from:
            return False
        if self.date_to is not None and tx.date > self.date_to:
            return False
        if self.category is not None and tx.category != Category.normalize_name(self.category):
            return False
        if self.type is not None and tx.type != self.type:
            return False
        if self.keyword is not None and self.keyword.lower() not in tx.memo.lower():
            return False
        if self.tag is not None and self.tag.strip().lower() not in (t.lower() for t in tx.tags):
            return False
        return True
