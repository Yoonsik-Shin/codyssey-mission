from dataclasses import dataclass, field
from datetime import date
from .category import Category
from .period import Month
from .transaction import Transaction, TransactionType


@dataclass
class RecurringRule:
    """
    반복 내역 규칙 (예: 매월 25일 월급, 매월 1일 월세).
    특정 월에 적용하면 그 달의 거래(Transaction)를 만들어 냅니다.
    """
    type: TransactionType
    category: str
    amount: int
    day: int                      # 매월 며칠 (1~31). 그 달에 없는 날이면 말일로 보정
    memo: str = ""
    tags: list[str] = field(default_factory=list)
    id: str = ""                  # Repository.save()가 채번 (RC-0001)

    def __post_init__(self):
        """타입 변환만 담당 — Repository 역직렬화 시에도 호출됨 (Transaction과 같은 규칙)"""
        if isinstance(self.type, str):
            self.type = TransactionType(self.type.strip().lower())
        self.amount = int(self.amount)
        self.day = int(self.day)
        if isinstance(self.tags, str):
            self.tags = [t.strip() for t in self.tags.split(",") if t.strip()]

    @classmethod
    def create(
        cls,
        type_val: TransactionType | str,
        category: str,
        amount: int,
        day: int,
        memo: str = "",
        tags: list[str] | str = "",
    ) -> "RecurringRule":
        """정적 팩토리 — 비즈니스 검증 + 정규화 후 생성"""
        if amount <= 0:
            raise ValueError(f"금액은 0보다 큰 양수여야 합니다: {amount}")
        if not 1 <= day <= 31:
            raise ValueError(f"반복 일자는 1~31 사이여야 합니다: {day}")

        cleaned_category = Category.normalize_name(category)
        if not cleaned_category:
            raise ValueError("카테고리는 비어있을 수 없습니다.")

        return cls(type=type_val, category=cleaned_category, amount=amount, day=day,
                   memo=memo.strip(), tags=tags)

    def occurrence_date(self, month: Month) -> date:
        """해당 월의 발생일. 31일 규칙을 2월에 적용하면 2월 말일(28/29일)"""
        return month.first_day.replace(day=min(self.day, month.last_day.day))

    def to_transaction(self, month: Month) -> Transaction:
        """해당 월에 생성할 거래. 검증은 Transaction.create가 다시 수행"""
        return Transaction.create(
            type_val=self.type,
            category=self.category,
            amount=self.amount,
            date_val=self.occurrence_date(month),
            memo=self.memo,
            tags=list(self.tags),
        )
