from ..models.recurring import RecurringRule
from ..repositories.recurring import RecurringRuleRepository


class ListRecurringRulesUseCase:
    """반복 내역 목록 조회 유스케이스"""

    def __init__(self, rule_repo: RecurringRuleRepository):
        self._rule_repo = rule_repo

    def execute(self) -> list[RecurringRule]:
        return self._rule_repo.find_all()
