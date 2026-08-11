import signal
import sys
from enum import IntEnum
from components.bonus_quiz_game import BonusQuizGame
from components.quiz_game import QuizGame
from utils.input_utils import InputUtils
from utils.output_utils import OutputUtils

class QuizMenu(IntEnum):
    START = 1
    ADD = 2
    LIST = 3
    SCORE = 4
    EXIT = 5
    DELETE = 6  # BonusQuizGame 전용

quiz_game = None

def signal_handler(sig, frame):
    """OS 시그널(SIGINT, SIGTERM) 수신 시 실행되는 안전 종료 핸들러. 데이터 저장은 finally에 위임."""
    sig_name = "SIGINT" if sig == signal.SIGINT else "SIGTERM"
    OutputUtils.print_lines("", f"⚠️ 시그널({sig_name})을 수신하여 데이터를 안전하게 저장하고 종료합니다.")
    sys.exit(0)

if __name__ == "__main__":
    # OS 시그널 등록 (평가 항목 #11)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        game_type = InputUtils.get_valid_int("어떤 게임을 플레이하시겠습니까? (1. 기본 퀴즈 게임, 2. 보너스 퀴즈 게임): ", 1, 2)
        if game_type == 1:
            quiz_game = QuizGame.init_quiz()
        else:
            quiz_game = BonusQuizGame.init_quiz()

        while True:
            menu = quiz_game.choice_menu()
            if menu == QuizMenu.START:
                quiz_game.start()
            elif menu == QuizMenu.ADD:
                quiz_game.add_quiz()
            elif menu == QuizMenu.LIST:
                quiz_game.list_quizzes()
            elif menu == QuizMenu.SCORE:
                quiz_game.get_score()
            elif menu == QuizMenu.EXIT:
                # 사용자 종료 확인 UX (평가 항목 #1)
                if InputUtils.get_confirm_yes_no("정말 퀴즈 게임을 종료하시겠습니까? (y/n): "):
                    OutputUtils.print_lines("👋 퀴즈 게임을 종료합니다. 다음에 또 만나요!")
                    break
            elif menu == QuizMenu.DELETE:
                if isinstance(quiz_game, BonusQuizGame):
                    quiz_game.remove_quiz()
    except (KeyboardInterrupt, EOFError):
        OutputUtils.print_lines("", "⚠️ 사용자 입력 인터럽트로 인해 프로그램을 안전하게 종료합니다.")
    finally:
        if quiz_game:
            quiz_game.close()