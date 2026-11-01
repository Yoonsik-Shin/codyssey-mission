import re
from abc import abstractmethod
from collections.abc import Iterable, Iterator
from dataclasses import replace
from typing import override
from .base import BaseRepository
from ..stores.base import BaseStore
from ..stores.sequence_file import SequenceFile
from ..models.transaction import Transaction, TransactionType

TRANSACTION_FIELDS = ["id", "type", "category", "amount", "date", "memo", "tags"]


class TransactionRepository(BaseRepository[Transaction]):
    """가계부 거래(Transaction) 전용 리포지토리 인터페이스"""

    @abstractmethod
    def stream(self) -> Iterator[Transaction]:
        """저장된 거래를 한 건씩 yield 합니다 (파일 전체를 메모리에 올리지 않음)."""

    @abstractmethod
    def save_many(self, entities: Iterable[Transaction]) -> list[Transaction]:
        """여러 거래를 한 번의 파일 쓰기로 저장합니다. ID가 없으면 채번합니다."""


class StoreTransactionRepository(TransactionRepository):
    """
    BaseStore(CsvStore, JsonlStore 등)를 주입받아
    Transaction 도메인 객체와 파일 원시 데이터 간의 변환 및 저장을 전담하는 구현체.
    ID 채번도 이 레이어가 책임집니다.
    """

    def __init__(self, store: BaseStore, sequence: SequenceFile):
        self._store = store
        self._sequence = sequence

    def _last_number(self) -> int:
        """
        마지막으로 발급한 ID 순번 반환.
        시퀀스 파일과 실제 레코드 중 큰 값을 써서, 시퀀스 파일이 없거나 뒤처져도 중복이 생기지 않게 함
        """
        max_num = self._sequence.read()
        for item in self._store.stream():
            match = re.match(r"^TX-(\d+)$", item.get("id", ""))
            if match:
                max_num = max(max_num, int(match.group(1)))
        return max_num

    @override
    def save(self, entity: Transaction) -> Transaction:
        """ID가 없으면 채번 후 파일 끝에 추가, 있으면 해당 행만 교체해 전체 재작성"""
        if not entity.id:
            next_num = self._last_number() + 1
            entity = replace(entity, id=f"TX-{next_num:06d}")
            self._store.append(self._to_dict(entity))
            self._sequence.write(next_num)
            return entity

        updated_row = self._to_dict(entity)
        self._store.save(
            updated_row if item.get("id") == entity.id else item
            for item in self._store.stream()
        )
        return entity

    @override
    def save_many(self, entities: Iterable[Transaction]) -> list[Transaction]:
        next_num = self._last_number() + 1
        saved = []
        for entity in entities:
            if not entity.id:
                entity = replace(entity, id=f"TX-{next_num:06d}")
                next_num += 1
            saved.append(entity)

        if not saved:
            return saved

        saved_by_id = {tx.id: tx for tx in saved}

        def merged_rows() -> Iterator[dict]:
            for item in self._store.stream():
                existing = saved_by_id.pop(item.get("id"), None)
                yield self._to_dict(existing) if existing else item
            for remaining in saved_by_id.values():
                yield self._to_dict(remaining)

        self._store.save(merged_rows())
        self._sequence.write(next_num - 1)
        return saved

    @override
    def stream(self) -> Iterator[Transaction]:
        for item in self._store.stream():
            yield self._to_entity(item)

    @override
    def find_all(self) -> list[Transaction]:
        """저장된 모든 데이터를 Transaction 도메인 객체 리스트로 반환"""
        return list(self.stream())

    @override
    def find_by_id(self, entity_id: str) -> Transaction | None:
        """특정 ID의 Transaction 객체 조회"""
        for item in self._store.stream():
            if item.get("id") == entity_id:
                return self._to_entity(item)
        return None

    @override
    def delete(self, entity_id: str) -> bool:
        """ID로 Transaction 삭제. 없는 ID면 파일을 건드리지 않고 False 반환"""
        if self.find_by_id(entity_id) is None:
            return False

        self._store.save(item for item in self._store.stream() if item.get("id") != entity_id)
        return True

    # -------------------------------------------------------------
    # Private 직렬화/역직렬화 헬퍼
    # -------------------------------------------------------------
    @staticmethod
    def _to_dict(entity: Transaction) -> dict:
        return {
            "id": entity.id,
            "type": entity.type.value,
            "category": entity.category,
            "amount": entity.amount,
            "date": entity.date.isoformat(),
            "memo": entity.memo,
            "tags": ",".join(entity.tags),
        }

    @staticmethod
    def _to_entity(data: dict) -> Transaction:
        try:
            return Transaction(
                id=data["id"],
                type=TransactionType(data["type"]),
                category=data.get("category", "미분류"),
                amount=int(data["amount"]),
                date=data["date"],
                memo=data.get("memo") or "",
                tags=data.get("tags") or "",  # "a,b" → ["a", "b"] 변환은 Transaction이 담당
            )
        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f"손상된 거래 데이터가 있습니다 (id={data.get('id', '?')}): {e}")
