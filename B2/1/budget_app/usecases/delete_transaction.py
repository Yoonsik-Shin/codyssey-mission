from ..errors import TransactionNotFoundError
from ..repositories.transaction import TransactionRepository


class DeleteTransactionUseCase:
    """거래 삭제 유스케이스. 없는 id면 TransactionNotFoundError"""

    def __init__(self, tx_repo: TransactionRepository):
        self._tx_repo = tx_repo

    def execute(self, tx_id: str) -> None:
        if not self._tx_repo.delete(tx_id):
            raise TransactionNotFoundError(tx_id)
