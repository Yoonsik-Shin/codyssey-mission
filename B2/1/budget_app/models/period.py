"""
기간(날짜 · 월) 도메인 규칙.
"이 앱에서 유효한 날짜/월이 무엇인가"를 한 곳에서 정의하고, 모델과 CLI가 함께 재사용합니다.
"""
import calendar
import re
from dataclasses import dataclass
from datetime import date

DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")
MONTH_PATTERN = re.compile(r"(\d{4})-(0[1-9]|1[0-2])")


def parse_date(value: str) -> date:
    """
    YYYY-MM-DD 문자열만 허용. date.fromisoformat은 3.11부터 '20240115', '2024-W03-1'도
    받아들이므로 형식을 정규식으로 먼저 고정합니다. 존재하지 않는 날짜(2024-02-30)도 거부됩니다.
    """
    cleaned = value.strip()
    try:
        if not DATE_PATTERN.fullmatch(cleaned):
            raise ValueError
        return date.fromisoformat(cleaned)
    except ValueError:
        raise ValueError(f"날짜 형식이 올바르지 않습니다: '{value}' (YYYY-MM-DD 형식이어야 합니다)")


@dataclass(frozen=True, order=True)
class Month:
    """
    연-월 값 객체 (예: 2024-01).
    문자열 대신 이 타입을 쓰면 '검증된 월'임이 타입으로 보장되고, 월 관련 계산이 한 곳에 모입니다.
    """
    year: int
    month: int

    def __post_init__(self):
        if not 1 <= self.month <= 12:
            raise ValueError(f"월은 1~12 사이여야 합니다: {self.month}")

    @classmethod
    def parse(cls, value: str) -> "Month":
        """'YYYY-MM' 문자열 → Month"""
        match = MONTH_PATTERN.fullmatch(value.strip())
        if not match:
            raise ValueError(f"월 형식이 올바르지 않습니다: '{value}' (YYYY-MM 형식 필요, 예: 2024-01)")
        return cls(year=int(match.group(1)), month=int(match.group(2)))

    @classmethod
    def of(cls, day: date) -> "Month":
        """날짜가 속한 월"""
        return cls(year=day.year, month=day.month)

    @property
    def first_day(self) -> date:
        return date(self.year, self.month, 1)

    @property
    def last_day(self) -> date:
        return date(self.year, self.month, calendar.monthrange(self.year, self.month)[1])

    def __str__(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"
