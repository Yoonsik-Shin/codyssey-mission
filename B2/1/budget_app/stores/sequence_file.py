import os
import tempfile
from .csv_file import replace_preserving_mode


class SequenceFile:
    """
    마지막으로 발급한 ID 순번을 파일에 기록합니다.
    가장 최근 거래를 삭제해도 같은 ID가 다시 발급되지 않도록 하기 위함입니다.
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def read(self) -> int:
        if not os.path.exists(self.filepath):
            return 0
        with open(self.filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()
        return int(content) if content.isdigit() else 0

    def write(self, value: int) -> None:
        dir_path = os.path.dirname(self.filepath) or "."
        os.makedirs(dir_path, exist_ok=True)
        fd, temp_path = tempfile.mkstemp(dir=dir_path, prefix=".tmp-", suffix=".seq")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(str(value))
        replace_preserving_mode(temp_path, self.filepath)
