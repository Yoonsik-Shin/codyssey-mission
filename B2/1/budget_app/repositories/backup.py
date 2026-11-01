from abc import ABC, abstractmethod
from typing import override
from ..models.backup import Backup
from ..stores.backup_store import DirectoryBackupStore


class BackupRepository(ABC):
    """백업 저장소 인터페이스 — 백업을 Backup 값 객체로 다룹니다."""

    @abstractmethod
    def create(self, name: str) -> Backup | None:
        """현재 데이터로 백업 생성. 백업할 파일이 없으면 None"""

    @abstractmethod
    def find_all(self) -> list[Backup]:
        """오래된 순서로 모든 백업"""

    @abstractmethod
    def find_by_name(self, name: str) -> Backup | None:
        """이름으로 백업 조회"""

    @abstractmethod
    def restore(self, backup: Backup) -> list[str]:
        """백업 시점으로 데이터 파일 복원. 복원한 파일명 반환"""


class StoreBackupRepository(BackupRepository):
    def __init__(self, store: DirectoryBackupStore):
        self._store = store

    @override
    def create(self, name: str) -> Backup | None:
        final_name, files = self._store.create(name)
        return Backup(name=final_name, files=tuple(files)) if files else None

    @override
    def find_all(self) -> list[Backup]:
        return [Backup(name=name, files=tuple(files)) for name, files in self._store.list_all()]

    @override
    def find_by_name(self, name: str) -> Backup | None:
        return next((b for b in self.find_all() if b.name == name), None)

    @override
    def restore(self, backup: Backup) -> list[str]:
        return self._store.restore(backup.name)
