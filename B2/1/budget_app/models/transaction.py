from datetime import date
from enum import auto, StrEnum
from dataclasses import dataclass, field
from .category import Category
from .period import parse_date


class TransactionType(StrEnum):
    INCOME = auto()
    EXPENSE = auto()


@dataclass
class Transaction:
    type: TransactionType
    category: str
    amount: int
    date: date
    memo: str = ""
    tags: list[str] = field(default_factory=list)
    id: str = ""  # Repository.save()가 채번 후 할당

    def __post_init__(self):
        """타입 변환만 담당 — Repository 역직렬화 시에도 안전하게 호출됨."""
        if isinstance(self.date, str):
            self.date = parse_date(self.date)
        elif not isinstance(self.date, date):
            raise TypeError(f"date는 date 객체 또는 YYYY-MM-DD 형식의 문자열이어야 합니다: {type(self.date)}")

        if isinstance(self.type, str):
            try:
                self.type = TransactionType(self.type.lower())
            except ValueError:
                raise ValueError(f"유효하지 않은 타입입니다: '{self.type}' (income 또는 expense 필요)")

        if isinstance(self.tags, str):
            self.tags = [t.strip() for t in self.tags.split(",") if t.strip()]

    def recency_key(self) -> tuple[date, str]:
        """최신순 정렬 키 — 날짜가 같으면 나중에 등록된(id가 큰) 거래가 더 최신"""
        return (self.date, self.id)

    @classmethod
    def create(
        cls,
        type_val: TransactionType | str,
        category: str,
        amount: int,
        date_val: date | str,
        memo: str = "",
        tags: list[str] | str = "",
    ) -> "Transaction":
        """
        정적 팩토리 메서드 — 비즈니스 검증 + 정규화 후 인스턴스 생성.
        ID는 Repository.save()가 채번하므로 포함하지 않습니다.
        """
        if amount <= 0:
            raise ValueError(f"금액은 0보다 큰 양수여야 합니다: {amount}")

        cleaned_category = Category.normalize_name(category)
        if not cleaned_category:
            raise ValueError("카테고리는 비어있을 수 없습니다.")

        return cls(
            type=type_val,
            category=cleaned_category,
            amount=amount,
            date=date_val,
            memo=memo.strip(),
            tags=tags,
        )
