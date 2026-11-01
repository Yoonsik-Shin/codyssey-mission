from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    도메인 객체(엔티티)의 영속성을 추상화하는 기본 리포지토리 인터페이스.
    외부 비즈니스 로직은 데이터가 파일, DB, 메모리 중 어디에 저장되는지 알 필요가 없습니다.
    """

    @abstractmethod
    def save(self, entity: T) -> T:
        """엔티티를 저장하거나 업데이트하고, 저장된 엔티티를 반환합니다."""

    @abstractmethod
    def find_all(self) -> list[T]:
        """모든 엔티티 목록을 조회합니다."""

    @abstractmethod
    def find_by_id(self, entity_id: str) -> T | None:
        """ID로 특정 엔티티를 단건 조회합니다."""

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """ID에 해당하는 엔티티를 삭제하고 성공 여부를 반환합니다."""

