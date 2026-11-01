from argparse import ArgumentParser, Namespace
from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """
    모든 CLI 명령어의 기본 추상 인터페이스.
    각 명령어는 name, help, setup_parser, execute를 구현해야 합니다.

    Command의 책임: 입력 형식 검증(argparse type / 대화형 재입력) + UseCase 호출 + 결과 출력.
    비즈니스 판단은 하지 않고, 필요한 UseCase만 생성자로 주입받습니다.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """명령어 이름 (예: 'add', 'list')"""

    @property
    @abstractmethod
    def help(self) -> str:
        """도움말 설명"""

    @abstractmethod
    def setup_parser(self, parser: ArgumentParser) -> ArgumentParser:
        """이 명령어에 필요한 인자(argument) 세팅"""

    @abstractmethod
    def execute(self, args: Namespace) -> None:
        """입력을 UseCase에 전달하고 결과를 출력"""
