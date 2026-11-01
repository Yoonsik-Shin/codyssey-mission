"""
데이터 파일 백업/복원 (stores 계층 — 도메인 객체를 모르고 폴더 이름과 파일명만 다룹니다).

<backup_dir>/<name>/transactions.csv ... 형태로 저장합니다.
"""
import os
import shutil
import tempfile
from .csv_file import replace_preserving_mode


class DirectoryBackupStore:
    def __init__(self, data_dir: str, backup_dir: str, filenames: list[str]):
        self.data_dir = data_dir
        self.backup_dir = backup_dir
        self.filenames = filenames  # 백업 대상(관리 중인) 데이터 파일 이름

    def create(self, name: str) -> tuple[str, list[str]]:
        """
        존재하는 데이터 파일을 임시 폴더에 모두 복사한 뒤 폴더 이름을 바꿔 확정합니다.
        복사 도중 실패해도 반쯤 만들어진 백업이 남지 않습니다. (확정된 이름, 복사한 파일) 반환
        """
        existing = [f for f in self.filenames if os.path.isfile(os.path.join(self.data_dir, f))]
        if not existing:
            return name, []

        os.makedirs(self.backup_dir, exist_ok=True)
        final_name = self._unique_name(name)
        temp_dir = tempfile.mkdtemp(dir=self.backup_dir, prefix=".tmp-")
        try:
            for filename in existing:
                shutil.copy2(os.path.join(self.data_dir, filename), os.path.join(temp_dir, filename))
            os.rename(temp_dir, os.path.join(self.backup_dir, final_name))
        except BaseException:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise
        return final_name, existing

    def list_all(self) -> list[tuple[str, list[str]]]:
        """(백업 이름, 파일 목록)을 이름순(=시간순)으로"""
        if not os.path.isdir(self.backup_dir):
            return []
        result = []
        for name in sorted(os.listdir(self.backup_dir), key=self._sort_key):
            path = os.path.join(self.backup_dir, name)
            if name.startswith(".") or not os.path.isdir(path):
                continue
            result.append((name, sorted(f for f in os.listdir(path) if f in self.filenames)))
        return result

    def restore(self, name: str) -> list[str]:
        """
        백업의 파일로 데이터 파일을 하나씩 원자적으로 교체합니다.
        백업 시점에 없던 관리 대상 파일은 지워 데이터 폴더를 백업 시점과 같게 맞춥니다.
        """
        source_dir = os.path.join(self.backup_dir, name)
        restored = []
        for filename in self.filenames:
            source = os.path.join(source_dir, filename)
            target = os.path.join(self.data_dir, filename)
            if os.path.isfile(source):
                fd, temp_path = tempfile.mkstemp(dir=self.data_dir, prefix=".tmp-")
                os.close(fd)
                try:
                    shutil.copyfile(source, temp_path)
                    replace_preserving_mode(temp_path, target)
                except BaseException:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise
                restored.append(filename)
            elif os.path.isfile(target):
                os.remove(target)
        return restored

    @staticmethod
    def _sort_key(name: str) -> tuple[str, int]:
        """'20240115-153000-10'이 '-2'보다 뒤에 오도록 접미사는 숫자로 비교"""
        base, _, suffix = name[:15], name[15:16], name[16:]
        return base, int(suffix) if suffix.isdigit() else 1

    def _unique_name(self, name: str) -> str:
        candidate, suffix = name, 2
        while os.path.exists(os.path.join(self.backup_dir, candidate)):
            candidate = f"{name}-{suffix}"
            suffix += 1
        return candidate
