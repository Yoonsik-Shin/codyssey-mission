from argparse import ArgumentParser, Namespace
from typing import override
from .base import BaseCommand
from ..decorators import log_execution
from ..usecases.add_category import AddCategoryUseCase
from ..usecases.list_categories import ListCategoriesUseCase
from ..usecases.remove_category import RemoveCategoryUseCase


class CategoryCommand(BaseCommand):
    def __init__(
        self,
        add_category: AddCategoryUseCase,
        list_categories: ListCategoriesUseCase,
        remove_category: RemoveCategoryUseCase,
    ):
        self._add_category = add_category
        self._list_categories = list_categories
        self._remove_category = remove_category

    @property
    def name(self) -> str:
        return "category"

    @property
    def help(self) -> str:
        return "카테고리 관리 (add/list/remove)"

    @override
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        # 하위 명령 없이 'category'만 실행하면 도움말 출력
        parser.set_defaults(handler=lambda _: parser.print_help())
        actions = parser.add_subparsers(metavar="{add,list,remove}")

        add_parser = actions.add_parser("add", help="카테고리 추가 (--name 생략 시 대화형 입력)")
        add_parser.add_argument('--name', type=str, help='카테고리명')
        add_parser.set_defaults(handler=self._add)

        list_parser = actions.add_parser("list", help="카테고리 목록")
        list_parser.set_defaults(handler=self._list)

        remove_parser = actions.add_parser("remove", help="카테고리 삭제")
        remove_parser.add_argument('--name', type=str, required=True, help='삭제할 카테고리명')
        remove_parser.add_argument(
            '--replace-with', type=str,
            help='사용 중인 카테고리일 때, 해당 거래들을 옮길 대체 카테고리',
        )
        remove_parser.set_defaults(handler=self._remove)
        return parser

    @override
    @log_execution
    def execute(self, args: Namespace) -> None:
        args.handler(args)

    def _add(self, args: Namespace) -> None:
        name = args.name if args.name is not None else input("카테고리명: ")
        category = self._add_category.execute(name)
        print(f"[저장 완료] category={category.name}")

    def _list(self, args: Namespace) -> None:
        for name in self._list_categories.execute():
            print(f"- {name}")

    def _remove(self, args: Namespace) -> None:
        result = self._remove_category.execute(args.name, replace_with=args.replace_with)
        if result.moved:
            print(f"[이동 완료] {result.moved}건의 거래를 '{result.replacement}'(으)로 옮겼습니다.")
        if result.moved_rules:
            print(f"[이동 완료] {result.moved_rules}건의 반복 내역을 '{result.replacement}'(으)로 옮겼습니다.")
        print(f"[삭제 완료] category={result.removed}")
