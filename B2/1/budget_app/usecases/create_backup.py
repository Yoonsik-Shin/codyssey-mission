from collections.abc import Callable
from datetime import datetime
from ..errors import NothingToBackupError
from ..models.backup import Backup
from ..repositories.backup import BackupRepository


class CreateBackupUseCase:
    """현재 데이터 파일 전체를 타임스탬프 이름으로 백업합니다."""

    def __init__(self, backup_repo: BackupRepository, now: Callable[[], datetime] = datetime.now):
        self._backup_repo = backup_repo
        self._now = now  # 테스트에서 시각을 고정할 수 있도록 주입

    def execute(self) -> Backup:
        backup = self._backup_repo.create(Backup.name_for(self._now()))
        if backup is None:
            raise NothingToBackupError()
        return backup
