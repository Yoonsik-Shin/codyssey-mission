from dataclasses import dataclass, field
from ..models.period import Month
from ..models.recurring import RecurringRule
from ..models.transaction import Transaction
from ..repositories.category import CategoryRepository
from ..repositories.recurring import RecurringRuleRepository
from ..repositories.transaction import TransactionRepository


@dataclass
class ApplyRecurringResult:
    month: Month
    created: list[tuple[RecurringRule, Transaction]] = field(default_factory=list)
    already_applied: list[RecurringRule] = field(default_factory=list)
    skipped: list[tuple[RecurringRule, str]] = field(default_factory=list)  # (규칙, 사유)


class ApplyRecurringRulesUseCase:
    """
    반복 내역 적용 유스케이스 — 특정 월의 거래를 규칙으로부터 생성합니다.

    - 같은 달에 여러 번 실행해도 규칙마다 한 번만 생성 (적용 기록으로 판단)
    - 31일 규칙은 짧은 달의 말일로 보정 (RecurringRule.occurrence_date)
    - 카테고리가 삭제되었거나 값이 잘못된 규칙은 사유와 함께 건너뜀
    - 생성할 거래는 한 번의 원자적 쓰기로 저장한 뒤 적용 기록을 남김
    """

    def __init__(
        self,
        rule_repo: RecurringRuleRepository,
        tx_repo: TransactionRepository,
        category_repo: CategoryRepository,
    ):
        self._rule_repo = rule_repo
        self._tx_repo = tx_repo
        self._category_repo = category_repo

    def execute(self, month: Month) -> ApplyRecurringResult:
        result = ApplyRecurringResult(month=month)
        applied = self._rule_repo.applied_rule_ids(month)
        category_names = {cat.name for cat in self._category_repo.find_all()}

        pending: list[tuple[RecurringRule, Transaction]] = []
        for rule in self._rule_repo.find_all():
            if rule.id in applied:
                result.already_applied.append(rule)
            elif rule.category not in category_names:
                result.skipped.append((rule, f"등록되지 않은 카테고리입니다: '{rule.category}'"))
            else:
                try:
                    pending.append((rule, rule.to_transaction(month)))
                except ValueError as e:
                    result.skipped.append((rule, str(e)))

        if pending:
            # 거래 저장(원자적)을 먼저 끝내고 기록을 남김. 기록 직전에 중단되면 재실행 시 중복될 수 있으나
            # 반대 순서(기록 먼저)는 거래가 영영 생성되지 않는 쪽이라 더 나쁨
            saved = self._tx_repo.save_many(tx for _, tx in pending)
            result.created = [(rule, tx) for (rule, _), tx in zip(pending, saved)]
            self._rule_repo.record_applied(month, ((rule.id, tx.id) for rule, tx in result.created))

        return result
