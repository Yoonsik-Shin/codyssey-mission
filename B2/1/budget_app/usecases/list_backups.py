from ..models.backup import Backup
from ..repositories.backup import BackupRepository


class ListBackupsUseCase:
    """백업 목록 (오래된 순)"""

    def __init__(self, backup_repo: BackupRepository):
        self._backup_repo = backup_repo

    def execute(self) -> list[Backup]:
        return self._backup_repo.find_all()
