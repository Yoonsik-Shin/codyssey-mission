from dataclasses import dataclass
from datetime import datetime

NAME_FORMAT = "%Y%m%d-%H%M%S"


@dataclass(frozen=True)
class Backup:
    """
    백업 한 벌 (값 객체).
    이름은 생성 시각 타임스탬프이며, 같은 초에 여러 번 만들면 '-2', '-3' 접미사가 붙습니다.
    """
    name: str
    files: tuple[str, ...]

    @staticmethod
    def name_for(moment: datetime) -> str:
        return moment.strftime(NAME_FORMAT)

    @property
    def created_at(self) -> datetime:
        """이름 앞 15자(YYYYMMDD-HHMMSS)가 생성 시각. 접미사(-2 등)는 무시"""
        return datetime.strptime(self.name[:15], NAME_FORMAT)
