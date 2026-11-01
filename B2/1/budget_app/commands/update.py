from argparse import ArgumentParser, Namespace
from typing import override
from .base import BaseCommand
from .arg_types import parse_date, parse_positive_int, parse_type
from ..decorators import log_execution
from ..usecases.update_transaction import UpdateTransactionUseCase


class UpdateCommand(BaseCommand):
    """거래 수정 — 옵션 기반(안 A)으로 고정. 지정한 필드만 바뀝니다."""

    def __init__(self, update_transaction: UpdateTransactionUseCase):
        self._update_transaction = update_transaction

    @property
    def name(self) -> str:
        return "update"

    @property
    def help(self) -> str:
        return "거래 수정 (옵션 방식, 지정한 필드만 변경)"

    @override
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument('--id', required=True, help='수정할 거래 id (예: TX-000001)')
        parser.add_argument('--date', type=parse_date, help='날짜 (YYYY-MM-DD)')
        parser.add_argument('--type', type=parse_type, help='타입 (income/expense)')
        parser.add_argument('--category', type=str, help='카테고리')
        parser.add_argument('--amount', type=parse_positive_int, help='금액(양수)')
        parser.add_argument('--memo', type=str, help='메모 (빈 문자열 ""로 지우기)')
        parser.add_argument('--tags', type=str, help='태그, 쉼표로 구분 (빈 문자열 ""로 지우기)')
        return parser

    @override
    @log_execution
    def execute(self, args: Namespace) -> None:
        updated = self._update_transaction.execute(
            tx_id=args.id.strip(),
            date_val=args.date,
            type_val=args.type,
            category=args.category,
            amount=args.amount,
            memo=args.memo,
            tags=args.tags,
        )
        print(f"[수정 완료] id={updated.id}")
