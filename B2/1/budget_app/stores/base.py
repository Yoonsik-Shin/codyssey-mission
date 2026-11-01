from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from typing import Any


class BaseStore(ABC):
    """모든 물리 저장소(JSONL, CSV 등)의 기본 추상 인터페이스"""

    @abstractmethod
    def exists(self) -> bool:
        """저장 파일이 실제로 존재하는지 여부"""

    @abstractmethod
    def stream(self) -> Iterator[dict[str, Any]]:
        """저장소의 원시 딕셔너리를 한 건씩 yield 합니다 (스트리밍 읽기)."""

    def load(self) -> list[dict[str, Any]]:
        """저장소의 원시 딕셔너리를 모두 읽어옵니다. 작은 파일(카테고리, 예산)용."""
        return list(self.stream())

    @abstractmethod
    def save(self, data: Iterable[dict[str, Any]]) -> None:
        """원시 딕셔너리들로 저장소 전체를 원자적으로 교체합니다."""

    @abstractmethod
    def append(self, item: dict[str, Any]) -> None:
        """원시 딕셔너리 한 건을 저장소 끝에 추가합니다."""
