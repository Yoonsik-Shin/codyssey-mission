from argparse import ArgumentParser, Namespace
from typing import override
from .base import BaseCommand
from .arg_types import parse_month, parse_positive_int
from ..decorators import log_execution
from .formatters import format_budget_status, format_won
from ..usecases.get_monthly_summary import GetMonthlySummaryUseCase, MonthlyReport

DEFAULT_TOP = 3


class SummaryCommand(BaseCommand):
    def __init__(self, monthly_summary: GetMonthlySummaryUseCase):
        self._monthly_summary = monthly_summary

    @property
    def name(self) -> str:
        return "summary"

    @property
    def help(self) -> str:
        return "월별 요약 (수입/지출/잔액, 지출 TOP N, 예산 사용률)"

    @override
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        parser.add_argument('--month', type=parse_month, required=True, help='요약할 월 (YYYY-MM)')
        parser.add_argument(
            '--top', type=parse_positive_int, default=DEFAULT_TOP,
            help=f'카테고리별 지출 TOP N (기본값: {DEFAULT_TOP})',
        )
        return parser

    @override
    @log_execution
    def execute(self, args: Namespace) -> None:
        report = self._monthly_summary.execute(args.month)
        summary = report.summary

        print(f"[{summary.month} 요약]")
        if summary.is_empty:
            print("데이터 없음")
            self._print_budget(report)
            return

        print(f"총 수입: {format_won(summary.total_income)}")
        print(f"총 지출: {format_won(summary.total_expense)}")
        print(f"잔액: {format_won(summary.balance)}")
        self._print_budget(report)

        top = summary.top_expense_categories(args.top)
        print(f"\n지출 TOP {args.top}")
        if not top:
            print("지출 내역 없음")
        for rank, (category, amount) in enumerate(top, start=1):
            print(f"{rank}) {category} {format_won(amount)}")

    @staticmethod
    def _print_budget(report: MonthlyReport) -> None:
        if report.budget_status is None:
            print("예산: 미설정 ('budget set --month ... --amount ...'로 설정)")
            return
        for line in format_budget_status(report.budget_status):
            print(line)
