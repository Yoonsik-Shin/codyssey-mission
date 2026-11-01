from abc import abstractmethod
from typing import override
from .base import BaseRepository
from ..stores.base import BaseStore
from ..models.budget import Budget
from ..models.period import Month


BUDGET_FIELDS = ["id", "month", "category", "amount"]


class BudgetRepository(BaseRepository[Budget]):
    """예산(Budget) 영속화 전용 리포지토리 인터페이스"""

    @abstractmethod
    def find_by_month(self, month: Month, category: str = "all") -> Budget | None:
        """월(+카테고리)로 예산 조회. 저장 키 형식은 구현체만 압니다."""


class StoreBudgetRepository(BudgetRepository):
    """BaseStore(CsvStore 등)를 통한 예산 데이터 CRUD 구현체"""

    def __init__(self, store: BaseStore):
        self._store = store

    @override
    def save(self, entity: Budget) -> Budget:
        items = self._store.load()
        entity_dict = {
            "id": entity.id,
            "month": str(entity.month),
            "category": entity.category,
            "amount": entity.amount,
        }

        for i, item in enumerate(items):
            if item.get("id") == entity.id:
                items[i] = entity_dict
                self._store.save(items)
                return entity

        items.append(entity_dict)
        self._store.save(items)
        return entity

    @override
    def find_all(self) -> list[Budget]:
        items = self._store.load()
        return [
            Budget(
                month=item["month"],
                amount=int(item["amount"]),
                category=item.get("category", "all"),
            )
            for item in items
            if item.get("id")
        ]

    @override
    def find_by_id(self, entity_id: str) -> Budget | None:
        """ID(예: '2024-01:all')로 예산 조회"""
        items = self._store.load()
        for item in items:
            if item.get("id") == entity_id:
                return Budget(
                    month=item["month"],
                    amount=int(item["amount"]),
                    category=item.get("category", "all"),
                )
        return None

    @override
    def find_by_month(self, month: Month, category: str = "all") -> Budget | None:
        target = category.strip().lower() or "all"
        for item in self._store.load():
            if item.get("month") == str(month) and item.get("category", "all") == target:
                return Budget(month=item["month"], amount=int(item["amount"]), category=target)
        return None

    @override
    def delete(self, entity_id: str) -> bool:
        items = self._store.load()
        new_items = [item for item in items if item.get("id") != entity_id]
        if len(new_items) != len(items):
            self._store.save(new_items)
            return True
        return False

