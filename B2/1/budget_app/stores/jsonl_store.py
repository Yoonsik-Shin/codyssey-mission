import json
import os
import tempfile
from collections.abc import Iterable, Iterator
from typing import Any, override
from .base import BaseStore
from .csv_file import replace_preserving_mode


class JsonlStore(BaseStore):
    """
    물리적인 JSONL (JSON Lines) 파일의 I/O를 전담하는 Store 클래스.
    줄 단위로 JSON 객체를 기록하며, 처음 읽거나 쓸 때 파일이 없으면 자동 생성 및 안내 메시지를 출력합니다.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    @override
    def exists(self) -> bool:
        return os.path.exists(self.filepath)

    def _ensure_file(self) -> None:
        """저장 파일이 존재하지 않으면 빈 파일 생성 및 안내 메시지 출력"""
        dir_path = os.path.dirname(self.filepath)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", encoding="utf-8"):
                pass  # 빈 파일 생성
            print(f"[안내] 저장 파일이 생성되었습니다: {self.filepath}")

    @override
    def stream(self) -> Iterator[dict[str, Any]]:
        """JSONL 파일에서 한 줄씩 JSON 객체를 yield 합니다."""
        self._ensure_file()
        with open(self.filepath, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    raise ValueError(f"손상된 데이터가 있습니다: {self.filepath} {line_no}번째 줄")

    @override
    def save(self, data: Iterable[dict[str, Any]]) -> None:
        """임시 파일에 한 줄씩 기록한 뒤 os.replace로 원본과 교체합니다 (원자적 저장)."""
        self._ensure_file()
        dir_path = os.path.dirname(self.filepath) or "."
        fd, temp_path = tempfile.mkstemp(dir=dir_path, prefix=".tmp-", suffix=".jsonl")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
            replace_preserving_mode(temp_path, self.filepath)
        except BaseException:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    @override
    def append(self, item: dict[str, Any]) -> None:
        self._ensure_file()
        with open(self.filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
