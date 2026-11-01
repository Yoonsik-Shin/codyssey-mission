from dataclasses import replace
from datetime import date
from ..errors import NothingToUpdateError, TransactionNotFoundError
from ..models.transaction import Transaction, TransactionType
from ..repositories.transaction import TransactionRepository
from ..repositories.category import CategoryRepository
from .category_guard import ensure_category_exists


class UpdateTransactionUseCase:
    """
    거래 수정 유스케이스.
    전달된 필드만 바꾸고, 나머지는 기존 값을 유지합니다.
    수정 후 값도 Transaction.create로 다시 검증합니다.
    """

    def __init__(self, tx_repo: TransactionRepository, category_repo: CategoryRepository):
        self._tx_repo = tx_repo
        self._category_repo = category_repo

    def execute(
        self,
        tx_id: str,
        date_val: date | None = None,
        type_val: TransactionType | None = None,
        category: str | None = None,
        amount: int | None = None,
        memo: str | None = None,
        tags: str | None = None,
    ) -> Transaction:
        if all(v is None for v in (date_val, type_val, category, amount, memo, tags)):
            raise NothingToUpdateError()

        current = self._tx_repo.find_by_id(tx_id)
        if current is None:
            raise TransactionNotFoundError(tx_id)

        if category is not None:
            category = ensure_category_exists(self._category_repo, category)

        updated = Transaction.create(
            type_val=type_val if type_val is not None else current.type,
            category=category if category is not None else current.category,
            amount=amount if amount is not None else current.amount,
            date_val=date_val if date_val is not None else current.date,
            memo=memo if memo is not None else current.memo,
            tags=tags if tags is not None else current.tags,
        )

        return self._tx_repo.save(replace(updated, id=current.id))
