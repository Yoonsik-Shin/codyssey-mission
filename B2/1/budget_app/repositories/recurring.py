import re
from abc import abstractmethod
from collections.abc import Iterable
from dataclasses import replace
from typing import override
from .base import BaseRepository
from ..models.period import Month
from ..models.recurring import RecurringRule
from ..stores.base import BaseStore
from ..stores.sequence_file import SequenceFile

RECURRING_FIELDS = ["id", "type", "category", "amount", "day", "memo", "tags"]
RECURRING_LOG_FIELDS = ["rule_id", "month", "transaction_id"]


class RecurringRuleRepository(BaseRepository[RecurringRule]):
    """반복 내역 규칙 + 적용 기록 리포지토리 인터페이스"""

    @abstractmethod
    def applied_rule_ids(self, month: Month) -> set[str]:
        """해당 월에 이미 적용된 규칙 id (중복 생성 방지용)"""

    @abstractmethod
    def record_applied(self, month: Month, entries: Iterable[tuple[str, str]]) -> None:
        """(규칙 id, 생성된 거래 id) 적용 기록 추가"""


class StoreRecurringRuleRepository(RecurringRuleRepository):
    """
    규칙은 recurring.csv, 적용 기록은 recurring_log.csv에 저장합니다.
    규칙 id(RC-0001)는 거래 id처럼 시퀀스 파일로 발급해 삭제 후에도 재사용하지 않습니다.
    """

    def __init__(self, rule_store: BaseStore, log_store: BaseStore, sequence: SequenceFile):
        self._rule_store = rule_store
        self._log_store = log_store
        self._sequence = sequence

    @override
    def save(self, entity: RecurringRule) -> RecurringRule:
        if not entity.id:
            next_num = max([self._sequence.read(), *self._existing_numbers()]) + 1
            entity = replace(entity, id=f"RC-{next_num:04d}")
            self._rule_store.append(self._to_dict(entity))
            self._sequence.write(next_num)
            return entity

        updated = self._to_dict(entity)
        self._rule_store.save(updated if item.get("id") == entity.id else item for item in self._rule_store.stream())
        return entity

    @override
    def find_all(self) -> list[RecurringRule]:
        return [self._to_entity(item) for item in self._rule_store.load()]

    @override
    def find_by_id(self, entity_id: str) -> RecurringRule | None:
        return next((rule for rule in self.find_all() if rule.id == entity_id), None)

    @override
    def delete(self, entity_id: str) -> bool:
        if self.find_by_id(entity_id) is None:
            return False
        self._rule_store.save(item for item in self._rule_store.stream() if item.get("id") != entity_id)
        return True

    @override
    def applied_rule_ids(self, month: Month) -> set[str]:
        return {item["rule_id"] for item in self._log_store.stream() if item.get("month") == str(month)}

    @override
    def record_applied(self, month: Month, entries: Iterable[tuple[str, str]]) -> None:
        for rule_id, tx_id in entries:
            self._log_store.append({"rule_id": rule_id, "month": str(month), "transaction_id": tx_id})

    def _existing_numbers(self) -> list[int]:
        numbers = []
        for item in self._rule_store.stream():
            match = re.match(r"^RC-(\d+)$", item.get("id", ""))
            if match:
                numbers.append(int(match.group(1)))
        return numbers

    @staticmethod
    def _to_dict(rule: RecurringRule) -> dict:
        return {
            "id": rule.id,
            "type": rule.type.value,
            "category": rule.category,
            "amount": rule.amount,
            "day": rule.day,
            "memo": rule.memo,
            "tags": ",".join(rule.tags),
        }

    @staticmethod
    def _to_entity(data: dict) -> RecurringRule:
        try:
            return RecurringRule(
                id=data["id"],
                type=data["type"],
                category=data["category"],
                amount=data["amount"],
                day=data["day"],
                memo=data.get("memo") or "",
                tags=data.get("tags") or "",
            )
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"손상된 반복 내역 데이터가 있습니다 (id={data.get('id', '?')}): {e}")
