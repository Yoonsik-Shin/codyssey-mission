from argparse import ArgumentParser, Namespace
from typing import override
from .base import BaseCommand
from .arg_types import ask, ask_category, parse_day, parse_month, parse_positive_int, parse_type
from .formatters import format_recurring_rules, format_won
from ..decorators import log_execution
from ..models.transaction import TransactionType
from ..usecases.add_recurring_rule import AddRecurringRuleUseCase
from ..usecases.apply_recurring_rules import ApplyRecurringRulesUseCase
from ..usecases.list_categories import ListCategoriesUseCase
from ..usecases.list_recurring_rules import ListRecurringRulesUseCase
from ..usecases.remove_recurring_rule import RemoveRecurringRuleUseCase


class RecurringCommand(BaseCommand):
    """반복 내역 (월급/월세 등) 등록 및 특정 월 자동 생성"""

    def __init__(
        self,
        add_rule: AddRecurringRuleUseCase,
        list_rules: ListRecurringRulesUseCase,
        remove_rule: RemoveRecurringRuleUseCase,
        apply_rules: ApplyRecurringRulesUseCase,
        list_categories: ListCategoriesUseCase,
    ):
        self._add_rule = add_rule
        self._list_rules = list_rules
        self._remove_rule = remove_rule
        self._apply_rules = apply_rules
        self._list_categories = list_categories

    @property
    def name(self) -> str:
        return "recurring"

    @property
    def help(self) -> str:
        return "반복 내역 관리 (add/list/remove/apply)"

    @override
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        parser.set_defaults(handler=lambda _: parser.print_help())
        actions = parser.add_subparsers(metavar="{add,list,remove,apply}")

        add_parser = actions.add_parser("add", help="반복 내역 등록 (생략한 항목은 대화형 입력)")
        add_parser.add_argument('--type', type=parse_type, help='타입 (income/expense)')
        add_parser.add_argument('--category', type=str, help='카테고리')
        add_parser.add_argument('--amount', type=parse_positive_int, help='금액(양수)')
        add_parser.add_argument('--day', type=parse_day, help='매월 며칠 (1~31, 없는 날은 말일)')
        add_parser.add_argument('--memo', type=str, help='메모(선택)')
        add_parser.add_argument('--tags', type=str, help='태그 (쉼표로 구분)')
        add_parser.set_defaults(handler=self._add)

        list_parser = actions.add_parser("list", help="반복 내역 목록")
        list_parser.set_defaults(handler=self._list)

        remove_parser = actions.add_parser("remove", help="반복 내역 삭제 (이미 생성된 거래는 유지)")
        remove_parser.add_argument('--id', required=True, help='삭제할 반복 내역 id (예: RC-0001)')
        remove_parser.set_defaults(handler=self._remove)

        apply_parser = actions.add_parser("apply", help="해당 월의 거래 생성 (여러 번 실행해도 중복 생성 없음)")
        apply_parser.add_argument('--month', type=parse_month, required=True, help='생성할 월 (YYYY-MM)')
        apply_parser.set_defaults(handler=self._apply)
        return parser

    @override
    @log_execution
    def execute(self, args: Namespace) -> None:
        args.handler(args)

    def _add(self, args: Namespace) -> None:
        type_val: TransactionType = args.type or ask(
            f"타입({'/'.join(t.value for t in TransactionType)}): ", parse_type
        )
        category = ask_category(self._list_categories.execute(), args.category)
        amount: int = args.amount or ask("금액(양수): ", parse_positive_int)
        day: int = args.day or ask("매월 며칠(1~31): ", parse_day)
        memo = args.memo if args.memo is not None else input("메모(선택): ")
        tags = args.tags if args.tags is not None else input("태그(쉼표로 구분, 없으면 엔터): ")

        rule = self._add_rule.execute(type_val=type_val, category=category, amount=amount,
                                      day=day, memo=memo, tags=tags)
        print(f"[저장 완료] id={rule.id} (매월 {rule.day}일 {rule.category} {format_won(rule.amount)})")

    def _list(self, args: Namespace) -> None:
        lines = format_recurring_rules(self._list_rules.execute())
        if not lines:
            print("등록된 반복 내역이 없습니다. 'recurring add'로 등록해 보세요.")
        for line in lines:
            print(line)

    def _remove(self, args: Namespace) -> None:
        self._remove_rule.execute(args.id.strip())
        print(f"[삭제 완료] id={args.id.strip()}")

    def _apply(self, args: Namespace) -> None:
        result = self._apply_rules.execute(args.month)
        for rule, tx in result.created:
            print(f"[생성] {tx.id} ← {rule.id} | {tx.date.isoformat()} | {tx.category} | {format_won(tx.amount)}")
        for rule in result.already_applied:
            print(f"[건너뜀] {rule.id}: {result.month}에 이미 생성됨")
        for rule, reason in result.skipped:
            print(f"⚠️  [건너뜀] {rule.id}: {reason}")
        print(f"[완료] {result.month} created={len(result.created)}, "
              f"already={len(result.already_applied)}, skipped={len(result.skipped)}")
