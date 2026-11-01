from argparse import ArgumentParser, Namespace
from typing import override
from .base import BaseCommand
from ..decorators import log_execution
from ..usecases.import_transactions import ImportTransactionsUseCase


class ImportCommand(BaseCommand):
    def __init__(self, import_transactions: ImportTransactionsUseCase):
        self._import_transactions = import_transactions

    @property
    def name(self) -> str:
        return "import"

    @property
    def help(self) -> str:
        return "CSV 파일에서 거래 일괄 등록"

    @override
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument(
            '--from', dest='source', required=True,
            help='가져올 CSV 경로 (헤더: date,type,category,amount[,memo,tags])',
        )
        return parser

    @override
    @log_execution
    def execute(self, args: Namespace) -> None:
        result = self._import_transactions.execute(args.source)
        for error in result.errors:
            print(f"⚠️  건너뜀 - {error}")
        print(f"[완료] imported={result.imported}, skipped={result.skipped}")
