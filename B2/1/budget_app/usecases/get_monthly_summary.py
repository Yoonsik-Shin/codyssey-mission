from dataclasses import dataclass
from ..models.budget import Budget, BudgetStatus
from ..models.period import Month
from ..models.summary import MonthlySummary
from ..repositories.budget import BudgetRepository
from ..repositories.transaction import TransactionRepository


@dataclass(frozen=True)
class MonthlyReport:
    summary: MonthlySummary
    budget: Budget | None
    budget_status: BudgetStatus | None  # 예산이 설정된 달만 존재


class GetMonthlySummaryUseCase:
    """
    월별 요약 유스케이스.
    거래를 스트리밍으로 집계하고, 해당 월 예산이 있으면 사용 현황을 함께 계산합니다.
    """

    def __init__(self, tx_repo: TransactionRepository, budget_repo: BudgetRepository):
        self._tx_repo = tx_repo
        self._budget_repo = budget_repo

    def execute(self, month: Month) -> MonthlyReport:
        summary = MonthlySummary.from_transactions(month, self._tx_repo.stream())
        budget = self._budget_repo.find_by_month(month)
        budget_status = budget.evaluate(summary.total_expense) if budget else None

        return MonthlyReport(summary=summary, budget=budget, budget_status=budget_status)
