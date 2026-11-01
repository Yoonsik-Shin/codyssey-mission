from ..models.recurring import RecurringRule
from ..models.transaction import TransactionType
from ..repositories.category import CategoryRepository
from ..repositories.recurring import RecurringRuleRepository
from .category_guard import ensure_category_exists


class AddRecurringRuleUseCase:
    """반복 내역 등록 유스케이스. 카테고리 존재 확인 후 규칙을 저장합니다."""

    def __init__(self, rule_repo: RecurringRuleRepository, category_repo: CategoryRepository):
        self._rule_repo = rule_repo
        self._category_repo = category_repo

    def execute(
        self,
        type_val: TransactionType | str,
        category: str,
        amount: int,
        day: int,
        memo: str = "",
        tags: list[str] | str = "",
    ) -> RecurringRule:
        rule = RecurringRule.create(
            type_val=type_val,
            category=ensure_category_exists(self._category_repo, category),
            amount=amount,
            day=day,
            memo=memo,
            tags=tags,
        )
        return self._rule_repo.save(rule)
