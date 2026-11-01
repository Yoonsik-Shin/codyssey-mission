import csv
import os
from collections.abc import Iterable, Iterator
from typing import Any, override
from .base import BaseStore
from .csv_file import read_csv_rows, write_csv_rows


class CsvStore(BaseStore):
    """
    물리적인 CSV 파일의 I/O를 전담하는 Store 클래스.
    처음 읽거나 쓸 때 파일이 없으면 디렉토리와 파일을 자동 생성하고 초기화 안내 메시지를 출력합니다.
    생성자에서는 파일을 건드리지 않으므로, 객체를 만들어 두기만 해도(--help 등) 부작용이 없습니다.
    """

    def __init__(self, filepath: str, fieldnames: list[str]):
        self.filepath = filepath
        self.fieldnames = fieldnames

    @override
    def exists(self) -> bool:
        return os.path.exists(self.filepath)

    def _ensure_file(self) -> None:
        """저장 파일이 존재하지 않으면 헤더가 포함된 빈 CSV 파일 생성 및 안내 메시지 출력"""
        if not os.path.exists(self.filepath):
            write_csv_rows(self.filepath, self.fieldnames, [])
            print(f"[안내] 저장 파일이 생성되었습니다: {self.filepath}")

    @override
    def stream(self) -> Iterator[dict[str, Any]]:
        """CSV 파일에서 행(Row)을 한 줄씩 딕셔너리로 yield 합니다."""
        self._ensure_file()
        yield from read_csv_rows(self.filepath)

    @override
    def save(self, data: Iterable[dict[str, Any]]) -> None:
        """임시 파일에 쓴 뒤 원본과 교체합니다. data가 제너레이터여도 됩니다."""
        write_csv_rows(self.filepath, self.fieldnames, data)

    @override
    def append(self, item: dict[str, Any]) -> None:
        """파일 끝에 한 행을 추가합니다. 전체 재작성 없이 O(1)로 동작합니다."""
        self._ensure_file()
        with open(self.filepath, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames, extrasaction="ignore")
            writer.writerow(item)
