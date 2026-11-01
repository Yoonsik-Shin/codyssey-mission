import heapq
from ..models.transaction import Transaction
from ..models.transaction_query import TransactionQuery
from ..repositories.transaction import TransactionRepository


class SearchTransactionsUseCase:
    """
    거래 검색 유스케이스.
    스트리밍으로 읽으며 조건에 맞는 거래만 남기고, 결과를 최신순으로 반환합니다.
    메모리에는 파일 전체가 아니라 '조건에 맞는 거래'(limit 지정 시 최대 limit건)만 올라갑니다.
    """

    def __init__(self, tx_repo: TransactionRepository):
        self._tx_repo = tx_repo

    def execute(self, query: TransactionQuery, limit: int | None = None) -> list[Transaction]:
        matched = (tx for tx in self._tx_repo.stream() if query.matches(tx))
        if limit is not None:
            return heapq.nlargest(limit, matched, key=Transaction.recency_key)
        return sorted(matched, key=Transaction.recency_key, reverse=True)
