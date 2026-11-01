from argparse import ArgumentParser, Namespace
from typing import override
from .base import BaseCommand
from .arg_types import parse_date, parse_positive_int, parse_type
from ..decorators import log_execution
from .formatters import format_transactions
from ..models.transaction_query import TransactionQuery
from ..usecases.search_transactions import SearchTransactionsUseCase


class SearchCommand(BaseCommand):
    def __init__(self, search_transactions: SearchTransactionsUseCase):
        self._search_transactions = search_transactions

    @property
    def name(self) -> str:
        return "search"

    @property
    def help(self) -> str:
        return "조건으로 거래 검색 (최신순)"

    @override
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument('--from', dest='date_from', type=parse_date, help='시작일 (YYYY-MM-DD, 포함)')
        parser.add_argument('--to', dest='date_to', type=parse_date, help='종료일 (YYYY-MM-DD, 포함)')
        parser.add_argument('--category', type=str, help='카테고리')
        parser.add_argument('--type', type=parse_type, help='타입 (income/expense)')
        parser.add_argument('--q', type=str, help='메모 키워드 (부분 일치)')
        parser.add_argument('--tag', type=str, help='태그 (정확히 일치)')
        parser.add_argument('--limit', type=parse_positive_int, help='출력할 최대 건수 (기본값: 전체)')
        return parser

    @override
    @log_execution
    def execute(self, args: Namespace) -> None:
        query = TransactionQuery(
            date_from=args.date_from,
            date_to=args.date_to,
            category=args.category,
            type=args.type,
            keyword=args.q,
            tag=args.tag,
        )
        transactions = self._search_transactions.execute(query, limit=args.limit)
        if not transactions:
            print("조건에 맞는 거래가 없습니다.")
            return

        for line in format_transactions(transactions):
            print(line)
        print(f"\n총 {len(transactions)}건")
