from argparse import ArgumentParser, Namespace
from typing import override
from .base import BaseCommand
from .formatters import format_backups
from ..decorators import log_execution
from ..usecases.create_backup import CreateBackupUseCase
from ..usecases.list_backups import ListBackupsUseCase
from ..usecases.restore_backup import RestoreBackupUseCase


class BackupCommand(BaseCommand):
    """데이터 파일 백업/복원 — 'backup'만 실행하면 백업 생성"""

    def __init__(
        self,
        create_backup: CreateBackupUseCase,
        list_backups: ListBackupsUseCase,
        restore_backup: RestoreBackupUseCase,
    ):
        self._create_backup = create_backup
        self._list_backups = list_backups
        self._restore_backup = restore_backup

    @property
    def name(self) -> str:
        return "backup"

    @property
    def help(self) -> str:
        return "데이터 백업 생성 (list/restore로 조회·복원)"

    @override
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        # 하위 명령 없이 'backup'만 실행하면 백업 생성 (요구사항: backup 실행 시 타임스탬프 백업 생성)
        parser.set_defaults(handler=self._create)
        actions = parser.add_subparsers(metavar="{list,restore}")

        list_parser = actions.add_parser("list", help="백업 목록")
        list_parser.set_defaults(handler=self._list)

        restore_parser = actions.add_parser("restore", help="백업 시점으로 복원 (복원 전 현재 상태를 자동 백업)")
        restore_parser.add_argument('--name', required=True, help='복원할 백업 이름 (backup list 참고)')
        restore_parser.add_argument('--yes', action='store_true', help='확인 질문 없이 복원')
        restore_parser.set_defaults(handler=self._restore)
        return parser

    @override
    @log_execution
    def execute(self, args: Namespace) -> None:
        args.handler(args)

    def _create(self, args: Namespace) -> None:
        backup = self._create_backup.execute()
        print(f"[백업 완료] {backup.name} ({len(backup.files)} files: {', '.join(backup.files)})")

    def _list(self, args: Namespace) -> None:
        lines = format_backups(self._list_backups.execute())
        if not lines:
            print("백업이 없습니다. 'backup'으로 백업을 만들어 보세요.")
        for line in lines:
            print(line)

    def _restore(self, args: Namespace) -> None:
        if not args.yes:
            answer = input(f"현재 데이터를 '{args.name}' 시점으로 되돌립니다. 계속할까요? (y/N): ")
            if answer.strip().lower() not in ("y", "yes"):
                print("[취소] 복원하지 않았습니다.")
                return

        result = self._restore_backup.execute(args.name)
        if result.safety_backup is not None:
            print(f"[안내] 복원 전 상태를 '{result.safety_backup.name}'(으)로 백업했습니다.")
        print(f"[복원 완료] {result.restored.name} ({', '.join(result.files)})")
