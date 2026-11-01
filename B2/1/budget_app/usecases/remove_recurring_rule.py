from ..errors import RecurringRuleNotFoundError
from ..repositories.recurring import RecurringRuleRepository


class RemoveRecurringRuleUseCase:
    """
    반복 내역 삭제 유스케이스.
    규칙만 지우며, 이미 생성된 거래는 그대로 둡니다 (과거 기록 보존).
    """

    def __init__(self, rule_repo: RecurringRuleRepository):
        self._rule_repo = rule_repo

    def execute(self, rule_id: str) -> None:
        if not self._rule_repo.delete(rule_id):
            raise RecurringRuleNotFoundError(rule_id)
