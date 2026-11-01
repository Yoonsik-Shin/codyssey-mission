"""
import/export 전용 거래 CSV 어댑터 (Repository 계층).
util이 아니라 UseCase에 주입되는 협력 객체로, 외부 CSV 스키마와 도메인 객체 사이를 변환합니다.
실제 파일 I/O는 stores.csv_file에 위임합니다.
"""
import os
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from ..errors import InvalidCsvHeaderError, SourceFileNotFoundError
from ..models.transaction import Transaction
from ..stores.csv_file import read_csv_header, read_csv_rows, write_csv_rows

CSV_COLUMNS = ["date", "type", "category", "amount", "memo", "tags"]
REQUIRED_COLUMNS = ["date", "type", "category", "amount"]


@dataclass(frozen=True)
class CsvRow:
    """CSV 한 행의 변환 결과 — 성공하면 transaction, 실패하면 error에 사유"""
    line_no: int
    transaction: Transaction | None = None
    error: str | None = None


class TransactionCsvFile:
    """
    import/export용 거래 CSV 형식을 전담합니다 (Repository 계층: 도메인 객체 ↔ 행 변환).
    스키마(컬럼), 헤더 검증, 행 ↔ Transaction 변환을 알고, 비즈니스 흐름은 모릅니다.
    """

    def read(self, filepath: str) -> Iterator[CsvRow]:
        """
        파일과 헤더를 먼저 검증한 뒤, 행을 한 줄씩 변환해 yield 하는 스트림을 반환합니다.
        (제너레이터 함수로 만들면 검증이 첫 next() 때로 미뤄지므로 일반 함수로 감쌈)
        """
        if not os.path.isfile(filepath):
            raise SourceFileNotFoundError(filepath)

        header = read_csv_header(filepath)
        missing = [col for col in REQUIRED_COLUMNS if col not in header]
        if missing:
            raise InvalidCsvHeaderError(missing, REQUIRED_COLUMNS)

        return self._parse_rows(filepath)

    def write(self, filepath: str, transactions: Iterable[Transaction]) -> int:
        """거래를 CSV 스키마로 원자적으로 기록하고 건수를 반환합니다."""
        return write_csv_rows(filepath, CSV_COLUMNS, (self._to_row(tx) for tx in transactions))

    def _parse_rows(self, filepath: str) -> Iterator[CsvRow]:
        # 헤더가 1번째 줄이므로 데이터는 2번째 줄부터
        for line_no, row in enumerate(read_csv_rows(filepath), start=2):
            try:
                yield CsvRow(line_no=line_no, transaction=self._to_transaction(row))
            except ValueError as e:
                yield CsvRow(line_no=line_no, error=str(e))

    @staticmethod
    def _to_transaction(row: dict) -> Transaction:
        raw_amount = (row.get("amount") or "").strip()
        try:
            amount = int(raw_amount)
        except ValueError:
            raise ValueError(f"금액이 정수가 아닙니다: '{raw_amount}'")

        return Transaction.create(
            type_val=(row.get("type") or "").strip(),
            category=row.get("category") or "",
            amount=amount,
            date_val=row.get("date") or "",
            memo=row.get("memo") or "",
            tags=row.get("tags") or "",
        )

    @staticmethod
    def _to_row(tx: Transaction) -> dict:
        return {
            "date": tx.date.isoformat(),
            "type": tx.type.value,
            "category": tx.category,
            "amount": tx.amount,
            "memo": tx.memo,
            "tags": ",".join(tx.tags),
        }
