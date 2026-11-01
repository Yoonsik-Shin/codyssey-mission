from ..models.budget import Budget
from ..models.period import Month
from ..repositories.budget import BudgetRepository


class SetBudgetUseCase:
    """
    예산 설정 유스케이스.
    특정 월(및 카테고리)의 예산을 새로 저장하거나 갱신합니다.
    """

    def __init__(self, budget_repo: BudgetRepository):
        self._budget_repo = budget_repo

    def execute(self, month: Month | str, amount: int, category: str = "all") -> Budget:
        budget = Budget(month=month, amount=amount, category=category)
        return self._budget_repo.save(budget)
