from dataclasses import dataclass, replace
from ..errors import CategoryInUseError, CategoryNotFoundError, SameReplacementCategoryError
from ..models.category import Category
from ..repositories.category import CategoryRepository
from ..repositories.recurring import RecurringRuleRepository
from ..repositories.transaction import TransactionRepository
from .category_guard import ensure_category_exists


@dataclass(frozen=True)
class RemoveCategoryResult:
    removed: str                    # 정규화된 삭제 카테고리명
    moved: int = 0                  # 대체 카테고리로 옮긴 거래 수
    moved_rules: int = 0            # 대체 카테고리로 옮긴 반복 내역 수
    replacement: str | None = None  # 정규화된 대체 카테고리명


class RemoveCategoryUseCase:
    """
    카테고리 삭제 유스케이스.
    거래나 반복 내역이 사용 중인 카테고리는 대체 카테고리(replace_with)가 주어져야만 삭제하며,
    이때 해당 거래/반복 내역의 카테고리를 대체 카테고리로 일괄 변경합니다.
    """

    def __init__(
        self,
        category_repo: CategoryRepository,
        tx_repo: TransactionRepository,
        rule_repo: RecurringRuleRepository,
    ):
        self._category_repo = category_repo
        self._tx_repo = tx_repo
        self._rule_repo = rule_repo

    def execute(self, name: str, replace_with: str | None = None) -> RemoveCategoryResult:
        target = Category.normalize_name(name)
        if self._category_repo.find_by_id(target) is None:
            raise CategoryNotFoundError(target, [cat.name for cat in self._category_repo.find_all()])

        in_use = [tx for tx in self._tx_repo.stream() if tx.category == target]
        rules_in_use = [rule for rule in self._rule_repo.find_all() if rule.category == target]
        if not in_use and not rules_in_use:
            self._category_repo.delete(target)
            return RemoveCategoryResult(removed=target)

        if replace_with is None:
            raise CategoryInUseError(target, len(in_use), len(rules_in_use))

        replacement = ensure_category_exists(self._category_repo, replace_with)
        if replacement == target:
            raise SameReplacementCategoryError(target)

        # 사용처 이동을 먼저 끝낸 뒤 카테고리를 지워, 중간에 실패해도 '존재하지 않는 카테고리'를 가진 데이터가 남지 않게 함
        if in_use:
            self._tx_repo.save_many(replace(tx, category=replacement) for tx in in_use)
        for rule in rules_in_use:
            self._rule_repo.save(replace(rule, category=replacement))
        self._category_repo.delete(target)
        return RemoveCategoryResult(
            removed=target, moved=len(in_use), moved_rules=len(rules_in_use), replacement=replacement,
        )
