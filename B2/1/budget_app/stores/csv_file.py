"""
stores 계층 내부 헬퍼 — CSV 파일 입출력과 원자적 교체의 공통 부분.
CsvStore(저장 파일)와 TransactionCsvFile(import/export 파일)이 함께 씁니다.
도메인 객체는 모르고 dict 행만 다룹니다.
"""
import csv
import os
import tempfile
from collections.abc import Iterable, Iterator
from typing import Any


def read_csv_rows(filepath: str) -> Iterator[dict[str, Any]]:
    """
    CSV 파일을 한 줄씩 읽어 딕셔너리로 yield 하는 제너레이터.
    파일 전체를 메모리에 올리지 않으므로 대용량 파일도 일정한 메모리로 처리할 수 있습니다.
    """
    with open(filepath, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            yield dict(row)


def read_csv_header(filepath: str) -> list[str]:
    """CSV 파일의 헤더(컬럼명)만 읽어옵니다."""
    with open(filepath, "r", encoding="utf-8", newline="") as f:
        return next(csv.reader(f), [])


def replace_preserving_mode(temp_path: str, target_path: str) -> None:
    """
    임시 파일로 원본을 원자적으로 교체합니다.
    mkstemp는 권한 600으로 파일을 만들므로, 기존 파일 권한(없으면 umask 기준 기본값)을 먼저 맞춥니다.
    """
    if os.path.exists(target_path):
        mode = os.stat(target_path).st_mode & 0o777
    else:
        umask = os.umask(0)
        os.umask(umask)
        mode = 0o666 & ~umask
    os.chmod(temp_path, mode)
    os.replace(temp_path, target_path)


def write_csv_rows(filepath: str, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> int:
    """
    rows를 임시 파일에 모두 기록한 뒤 os.replace로 원본과 교체합니다 (원자적 저장).
    쓰는 도중 오류가 나도 원본 파일은 그대로 남습니다. 기록한 행 수를 반환합니다.
    """
    dir_path = os.path.dirname(filepath) or "."
    os.makedirs(dir_path, exist_ok=True)

    fd, temp_path = tempfile.mkstemp(dir=dir_path, prefix=".tmp-", suffix=".csv")
    try:
        count = 0
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
                count += 1
            f.flush()
            os.fsync(f.fileno())
        replace_preserving_mode(temp_path, filepath)
        return count
    except BaseException:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
