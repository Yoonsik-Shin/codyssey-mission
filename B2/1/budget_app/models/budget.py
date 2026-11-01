from dataclasses import dataclass
from .period import Month


@dataclass
class Budget:
    month: Month    # 'YYYY-MM' 문자열을 넘기면 Month로 변환
    amount: int     # 예산 금액 (양수)
    category: str = "all"  # 특정 카테고리 예산 또는 전체("all")

    def __post_init__(self):
        if not isinstance(self.month, Month):
            self.month = Month.parse(self.month)

        if self.amount <= 0:
            raise ValueError(f"예산 금액은 0보다 큰 양수여야 합니다: {self.amount}")

        self.category = self.category.strip().lower() if self.category else "all"

    @property
    def id(self) -> str:
        """복합 키 형태의 고유 식별자 (예: 2024-01:all, 2024-01:food)"""
        return f"{self.month}:{self.category}"

    def evaluate(self, spent: int) -> "BudgetStatus":
        """실제 지출액을 받아 예산 대비 사용 현황을 계산"""
        return BudgetStatus(budget=self.amount, spent=spent)


@dataclass(frozen=True)
class BudgetStatus:
    """예산 대비 지출 현황 (값 객체)"""
    budget: int
    spent: int

    @property
    def remaining(self) -> int:
        return self.budget - self.spent

    @property
    def usage_percent(self) -> float:
        return round(self.spent / self.budget * 100, 1)

    @property
    def is_exceeded(self) -> bool:
        return self.spent > self.budget
