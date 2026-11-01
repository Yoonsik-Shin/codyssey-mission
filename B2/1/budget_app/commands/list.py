from argparse import ArgumentParser, Namespace
from typing import override
from .base import BaseCommand
from .arg_types import parse_positive_int
from ..decorators import log_execution
from .formatters import format_transactions
from ..usecases.list_transactions import ListTransactionsUseCase

DEFAULT_LIMIT = 20


class ListCommand(BaseCommand):
    def __init__(self, list_transactions: ListTransactionsUseCase):
        self._list_transactions = list_transactions

    @property
    def name(self) -> str:
        return "list"

    @property
    def help(self) -> str:
        return "거래 목록 조회 (최신순)"

    @override
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument(
            '--limit', type=parse_positive_int, default=DEFAULT_LIMIT,
            help=f'출력할 최대 건수 (기본값: {DEFAULT_LIMIT})',
        )
        return parser

    @override
    @log_execution
    def execute(self, args: Namespace) -> None:
        transactions = self._list_transactions.execute(limit=args.limit)
        if not transactions:
            print("등록된 거래가 없습니다. 'add' 명령으로 거래를 추가해 보세요.")
            return

        for line in format_transactions(transactions):
            print(line)
