from argparse import ArgumentTypeError
from collections.abc import Callable
from datetime import date
from typing import TypeVar
from ..models.period import Month, parse_date as parse_iso_date
from ..models.transaction import TransactionType

T = TypeVar("T")


def parse_date(value: str) -> date:
    try:
        return parse_iso_date(value)
    except ValueError:
        raise ArgumentTypeError(f"날짜 형식이 올바르지 않습니다: '{value}' (YYYY-MM-DD 형식, 예: 2024-01-15)")


def parse_month(value: str) -> Month:
    try:
        return Month.parse(value)
    except ValueError:
        raise ArgumentTypeError(f"월 형식이 올바르지 않습니다: '{value}' (YYYY-MM 형식, 예: 2024-01)")


def parse_type(value: str) -> TransactionType:
    try:
        return TransactionType(value.strip().lower())
    except ValueError:
        valid_types = ", ".join(t.value for t in TransactionType)
        raise ArgumentTypeError(f"타입은 {valid_types} 중 하나여야 합니다 (입력값: '{value}')")


def parse_positive_int(value: str) -> int:
    try:
        val = int(value.strip())
    except ValueError:
        raise ArgumentTypeError(f"숫자만 입력 가능합니다: '{value}'")
    if val <= 0:
        raise ArgumentTypeError(f"0보다 큰 양수여야 합니다: {val}")
    return val


def ask(label: str, parse: Callable[[str], T]) -> T:
    """올바른 값이 들어올 때까지 대화형으로 재입력을 요구"""
    while True:
        raw = input(label)
        try:
            return parse(raw)
        except ArgumentTypeError as e:
            print(f"❌ {e}")
