from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from ..errors import BackupNotFoundError
from ..models.backup import Backup
from ..repositories.backup import BackupRepository


@dataclass(frozen=True)
class RestoreResult:
    restored: Backup
    files: list[str]
    safety_backup: Backup | None  # 복원 직전 상태 (복원을 되돌릴 때 사용)


class RestoreBackupUseCase:
    """
    백업 복원 유스케이스.
    복원 전에 현재 상태를 먼저 백업해 두므로, 잘못 복원해도 바로 되돌릴 수 있습니다.
    """

    def __init__(self, backup_repo: BackupRepository, now: Callable[[], datetime] = datetime.now):
        self._backup_repo = backup_repo
        self._now = now

    def execute(self, name: str) -> RestoreResult:
        target = self._backup_repo.find_by_name(name)
        if target is None:
            raise BackupNotFoundError(name, [b.name for b in self._backup_repo.find_all()])

        safety = self._backup_repo.create(Backup.name_for(self._now()))
        files = self._backup_repo.restore(target)
        return RestoreResult(restored=target, files=files, safety_backup=safety)
