from argparse import ArgumentParser, Namespace
from datetime import date
from typing import override
from .base import BaseCommand
from .arg_types import ask, ask_category, parse_date, parse_positive_int, parse_type
from ..decorators import log_execution
from ..models.transaction import TransactionType
from ..usecases.add_transaction import AddTransactionUseCase
from ..usecases.list_categories import ListCategoriesUseCase


class AddCommand(BaseCommand):
    """거래 추가 — 기본은 대화형 입력, 옵션으로 넘긴 항목은 묻지 않음"""

    def __init__(self, add_transaction: AddTransactionUseCase, list_categories: ListCategoriesUseCase):
        self._add_transaction = add_transaction
        self._list_categories = list_categories

    @property
    def name(self) -> str:
        return "add"

    @property
    def help(self) -> str:
        return "거래 추가 (대화형)"

    @override
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        type_options_str = "/".join(t.value for t in TransactionType)

        parser.add_argument('--date', type=parse_date, help='날짜 (YYYY-MM-DD)')
        parser.add_argument('--type', type=parse_type, help=f'타입 ({type_options_str})')
        parser.add_argument('--category', type=str, help='카테고리')
        parser.add_argument('--amount', type=parse_positive_int, help='금액(양수)')
        parser.add_argument('--memo', type=str, help='메모(선택)')
        parser.add_argument('--tags', type=str, help='태그 (쉼표로 구분)')

        return parser

    @override
    @log_execution
    def execute(self, args: Namespace) -> None:
        date_val: date = args.date or ask("날짜(YYYY-MM-DD): ", parse_date)
        type_val: TransactionType = args.type or ask(
            f"타입({'/'.join(t.value for t in TransactionType)}): ", parse_type
        )
        category = ask_category(self._list_categories.execute(), args.category)
        amount: int = args.amount or ask("금액(양수): ", parse_positive_int)
        memo = args.memo if args.memo is not None else input("메모(선택): ")
        tags = args.tags if args.tags is not None else input("태그(쉼표로 구분, 없으면 엔터): ")

        saved_tx = self._add_transaction.execute(
            date_val=date_val,
            type_val=type_val,
            category=category,
            amount=amount,
            memo=memo,
            tags=tags,
        )

        print(f"[저장 완료] id={saved_tx.id}")
