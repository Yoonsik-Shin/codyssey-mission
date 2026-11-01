import heapq
from ..models.transaction import Transaction
from ..repositories.transaction import TransactionRepository


class ListTransactionsUseCase:
    """
    거래 목록 조회 유스케이스.
    스트리밍으로 한 건씩 읽으면서 heapq로 최신 N건만 유지하므로
    메모리 사용량이 파일 크기가 아니라 limit에 비례합니다.
    """

    def __init__(self, tx_repo: TransactionRepository):
        self._tx_repo = tx_repo

    def execute(self, limit: int) -> list[Transaction]:
        return heapq.nlargest(limit, self._tx_repo.stream(), key=Transaction.recency_key)
