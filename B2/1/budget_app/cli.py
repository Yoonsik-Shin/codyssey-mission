import argparse
import logging
import sys
from collections.abc import Sequence
from .commands.base import BaseCommand
from .bootstrap import DEFAULT_DATA_DIR, build_commands
from .commands.error_handler import handle_errors


class HintArgumentParser(argparse.ArgumentParser):
    """
    argparse 인자 오류도 앱의 다른 오류와 같은 '[오류] 원인 + [힌트] 해결 방법' 형식으로 출력합니다.
    하위 명령 파서(add, category add ...)도 이 클래스를 그대로 물려받습니다.
    """

    def error(self, message: str):
        self.print_usage(sys.stderr)
        print(f"[오류] {message}", file=sys.stderr)
        print(f"[힌트] 'python -m {self.prog} --help'로 사용법을 확인하세요.", file=sys.stderr)
        sys.exit(2)


@handle_errors
def main(args: Sequence[str] | None = None) -> None:
    argv = list(sys.argv[1:] if args is None else args)

    commands = build_commands(_parse_data_dir(argv))
    argument_parser, command_map = _build_parser(commands)
    parsed_args = argument_parser.parse_args(argv)
    _configure_logging(parsed_args.verbose)

    if parsed_args.command in command_map:
        command_map[parsed_args.command].execute(parsed_args)
    else:
        argument_parser.print_help()


def _parse_data_dir(argv: list[str]) -> str:
    """
    의존성 조립에 필요한 --data-dir만 먼저 읽습니다.
    나머지 인자 검증과 --help 처리는 전체 파서가 담당합니다.
    """
    pre_parser = HintArgumentParser(prog="budget_app", add_help=False)
    pre_parser.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    known_args, _ = pre_parser.parse_known_args(argv)
    return known_args.data_dir


def _build_parser(commands: list[BaseCommand]) -> tuple[argparse.ArgumentParser, dict[str, BaseCommand]]:
    argument_parser = HintArgumentParser(
        prog="budget_app",
        description="가계부 앱 (개인 재정 관리 CLI 도구)"
    )
    argument_parser.add_argument(
        "--data-dir", default=DEFAULT_DATA_DIR,
        help=f"저장 파일 폴더 (기본값: {DEFAULT_DATA_DIR})",
    )
    argument_parser.add_argument(
        "--verbose", action="store_true",
        help="실행 로그와 소요 시간 출력",
    )

    subparsers = argument_parser.add_subparsers(
        dest="command",
        help="실행할 명령어를 선택하세요"
    )

    command_map = {}
    for cmd in commands:
        cmd_parser = subparsers.add_parser(cmd.name, help=cmd.help, description=cmd.help)
        cmd.setup_parser(cmd_parser)
        command_map[cmd.name] = cmd

    return argument_parser, command_map


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        format="[로그] %(message)s",
        stream=sys.stderr,
    )
