from ..models.transaction_query import TransactionQuery
from ..repositories.transaction import TransactionRepository
from ..repositories.transaction_csv import TransactionCsvFile


class ExportTransactionsUseCase:
    """
    CSV 내보내기 유스케이스.
    조건에 맞는 거래를 스트리밍으로 읽어 바로 파일에 기록합니다 (import와 같은 스키마).
    """

    def __init__(self, tx_repo: TransactionRepository, csv_file: TransactionCsvFile):
        self._tx_repo = tx_repo
        self._csv_file = csv_file

    def execute(self, filepath: str, query: TransactionQuery) -> int:
        """기록한 거래 건수를 반환"""
        return self._csv_file.write(filepath, (tx for tx in self._tx_repo.stream() if query.matches(tx)))
