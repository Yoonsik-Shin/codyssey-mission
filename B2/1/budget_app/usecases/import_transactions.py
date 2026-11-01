from dataclasses import dataclass, field
from ..models.transaction import Transaction
from ..repositories.category import CategoryRepository
from ..repositories.transaction import TransactionRepository
from ..repositories.transaction_csv import TransactionCsvFile


@dataclass
class ImportResult:
    imported: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)  # 건너뛴 행의 사유


class ImportTransactionsUseCase:
    """
    CSV 가져오기 유스케이스.
    행 변환(형식 검증)은 TransactionCsvFile이, 카테고리 등록 여부 검증과 저장은 이 UseCase가 맡습니다.
    잘못된 행은 사유와 함께 건너뛰고, 통과한 거래는 한 번의 원자적 쓰기로 저장해
    도중에 실패해도 일부만 반영되지 않습니다.
    """

    def __init__(
        self,
        tx_repo: TransactionRepository,
        category_repo: CategoryRepository,
        csv_file: TransactionCsvFile,
    ):
        self._tx_repo = tx_repo
        self._category_repo = category_repo
        self._csv_file = csv_file

    def execute(self, filepath: str) -> ImportResult:
        rows = self._csv_file.read(filepath)
        category_names = {cat.name for cat in self._category_repo.find_all()}
        result = ImportResult()
        valid: list[Transaction] = []

        for row in rows:
            if row.error is None and row.transaction.category not in category_names:
                row_error = f"등록되지 않은 카테고리입니다: '{row.transaction.category}'"
            else:
                row_error = row.error

            if row_error is not None:
                result.skipped += 1
                result.errors.append(f"{row.line_no}번째 줄: {row_error}")
            else:
                valid.append(row.transaction)

        result.imported = len(self._tx_repo.save_many(valid))
        return result
