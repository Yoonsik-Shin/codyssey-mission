from datetime import date
from ..models.transaction import Transaction, TransactionType
from ..repositories.transaction import TransactionRepository
from ..repositories.category import CategoryRepository
from .category_guard import ensure_category_exists


class AddTransactionUseCase:
    """
    거래 추가 유스케이스.
    카테고리 존재 여부 검증 후 Transaction을 생성하고 저장합니다.
    """

    def __init__(self, tx_repo: TransactionRepository, category_repo: CategoryRepository):
        self._tx_repo = tx_repo
        self._category_repo = category_repo

    def execute(
        self,
        date_val: date | str,
        type_val: TransactionType | str,
        category: str,
        amount: int,
        memo: str = "",
        tags: list[str] | str = "",
    ) -> Transaction:
        tx = Transaction.create(
            type_val=type_val,
            category=ensure_category_exists(self._category_repo, category),
            amount=amount,
            date_val=date_val,
            memo=memo,
            tags=tags,
        )

        return self._tx_repo.save(tx)
