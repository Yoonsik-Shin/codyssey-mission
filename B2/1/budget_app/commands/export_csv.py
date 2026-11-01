import os
from argparse import ArgumentParser, Namespace
from typing import override
from .base import BaseCommand
from .arg_types import parse_date, parse_month
from .error_handler import UsageError
from ..decorators import log_execution
from ..models.transaction_query import TransactionQuery
from ..usecases.export_transactions import ExportTransactionsUseCase


class ExportCommand(BaseCommand):
    def __init__(self, export_transactions: ExportTransactionsUseCase):
        self._export_transactions = export_transactions

    @property
    def name(self) -> str:
        return "export"

    @property
    def help(self) -> str:
        return "조건에 맞는 거래를 CSV로 내보내기"

    @override
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument('--out', required=True, help='저장할 CSV 경로')
        parser.add_argument('--month', type=parse_month, help='내보낼 월 (YYYY-MM)')
        parser.add_argument('--from', dest='date_from', type=parse_date, help='시작일 (YYYY-MM-DD, 포함)')
        parser.add_argument('--to', dest='date_to', type=parse_date, help='종료일 (YYYY-MM-DD, 포함)')
        return parser

    @override
    @log_execution
    def execute(self, args: Namespace) -> None:
        self._ensure_outside_data_dir(args.out, args.data_dir)
        count = self._export_transactions.execute(args.out, self._build_query(args))
        print(f"[완료] {args.out} ({count} records)")

    @staticmethod
    def _ensure_outside_data_dir(out: str, data_dir: str) -> None:
        """--out이 데이터 폴더 안이면 거부 — 예: --out data/transactions.csv가 원본을 덮어쓰는 사고 방지"""
        out_dir = os.path.dirname(os.path.realpath(out))
        if out_dir == os.path.realpath(data_dir):
            raise UsageError(
                f"데이터 폴더 안에는 내보낼 수 없습니다: {out}",
                hint=f"--out에 '{data_dir}' 밖의 경로를 지정하세요 (예: --out export.csv).",
            )

    @staticmethod
    def _build_query(args: Namespace) -> TransactionQuery:
        """옵션 조합 규칙(--month 또는 --from/--to 중 하나 필수)은 CLI 입력 형식 검증이라 Command에서 처리"""
        has_range = args.date_from is not None or args.date_to is not None

        if args.month and has_range:
            raise UsageError(
                "--month와 --from/--to는 함께 쓸 수 없습니다.",
                hint="월 단위는 --month, 기간 지정은 --from/--to 중 하나만 사용하세요.",
            )
        if args.month:
            return TransactionQuery.for_month(args.month)
        if has_range:
            return TransactionQuery(date_from=args.date_from, date_to=args.date_to)

        raise UsageError(
            "내보낼 기간 조건이 없습니다.",
            hint="--month YYYY-MM 또는 --from YYYY-MM-DD --to YYYY-MM-DD 를 지정하세요.",
        )
