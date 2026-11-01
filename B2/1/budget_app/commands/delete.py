from argparse import ArgumentParser, Namespace
from typing import override
from .base import BaseCommand
from ..decorators import log_execution
from ..usecases.delete_transaction import DeleteTransactionUseCase


class DeleteCommand(BaseCommand):
    def __init__(self, delete_transaction: DeleteTransactionUseCase):
        self._delete_transaction = delete_transaction

    @property
    def name(self) -> str:
        return "delete"

    @property
    def help(self) -> str:
        return "거래 삭제"

    @override
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument('--id', required=True, help='삭제할 거래 id (예: TX-000001)')
        return parser

    @override
    @log_execution
    def execute(self, args: Namespace) -> None:
        tx_id = args.id.strip()
        self._delete_transaction.execute(tx_id)
        print(f"[삭제 완료] id={tx_id}")
