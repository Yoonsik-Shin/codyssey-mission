from argparse import ArgumentParser, Namespace
from datetime import date
from typing import override
from .base import BaseCommand
from .arg_types import ask, parse_date, parse_positive_int, parse_type
from ..decorators import log_execution
from ..models.category import Category
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
        category = self._get_category(args.category)
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

    def _get_category(self, given: str | None) -> str:
        """
        등록된 카테고리가 들어올 때까지 재입력을 요구 (요구사항: 안내 후 재입력/등록 유도).
        최종 존재 검증은 UseCase가 다시 하므로, 여기서는 대화형 UX를 위한 사전 확인입니다.
        """
        category_names = self._list_categories.execute()
        candidate = given

        while True:
            if candidate is not None and Category.normalize_name(candidate) in category_names:
                return candidate

            if candidate is not None:
                print(f"❌ 등록되지 않은 카테고리입니다: '{candidate}'")
                print(f"💡 사용 가능한 카테고리: [{', '.join(category_names)}]")
                print("💡 (새 카테고리를 추가하려면 'category add'로 먼저 등록해 주세요.)")
            candidate = input("카테고리: ")
