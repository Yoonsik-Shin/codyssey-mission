from argparse import ArgumentParser, Namespace
from typing import override
from .base import BaseCommand
from .arg_types import parse_month, parse_positive_int
from ..decorators import log_execution
from .formatters import format_budget_status, format_won
from ..usecases.get_monthly_summary import GetMonthlySummaryUseCase
from ..usecases.set_budget import SetBudgetUseCase


class BudgetCommand(BaseCommand):
    def __init__(self, set_budget: SetBudgetUseCase, monthly_summary: GetMonthlySummaryUseCase):
        self._set_budget = set_budget
        self._monthly_summary = monthly_summary

    @property
    def name(self) -> str:
        return "budget"

    @property
    def help(self) -> str:
        return "월 예산 설정 및 조회 (set/show)"

    @override
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        # 하위 명령 없이 'budget'만 실행하면 도움말 출력
        parser.set_defaults(handler=lambda _: parser.print_help())
        actions = parser.add_subparsers(metavar="{set,show}")

        set_parser = actions.add_parser("set", help="월 예산 저장 (이미 있으면 갱신)")
        set_parser.add_argument('--month', type=parse_month, required=True, help='예산 월 (YYYY-MM)')
        set_parser.add_argument('--amount', type=parse_positive_int, required=True, help='예산 금액 (양수)')
        set_parser.set_defaults(handler=self._set)

        show_parser = actions.add_parser("show", help="월 예산과 사용률 조회")
        show_parser.add_argument('--month', type=parse_month, required=True, help='조회할 월 (YYYY-MM)')
        show_parser.set_defaults(handler=self._show)
        return parser

    @override
    @log_execution
    def execute(self, args: Namespace) -> None:
        args.handler(args)

    def _set(self, args: Namespace) -> None:
        budget = self._set_budget.execute(month=args.month, amount=args.amount)
        print(f"[저장 완료] {budget.month} 예산 {format_won(budget.amount)}")

    def _show(self, args: Namespace) -> None:
        report = self._monthly_summary.execute(args.month)
        if report.budget_status is None:
            print(f"{args.month} 예산이 설정되어 있지 않습니다.")
            return
        print(f"[{args.month}] 지출: {format_won(report.budget_status.spent)}")
        for line in format_budget_status(report.budget_status):
            print(line)
