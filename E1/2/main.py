from components.bonus_quiz_game import BonusQuizGame
from components.quiz_game import QuizGame
from utils.input_utils import InputUtils
from utils.output_utils import OutputUtils

if __name__ == "__main__":
    quiz_game = None
    game_type = None

    try:
        game_type = InputUtils.get_valid_int("어떤 게임을 플레이하시겠습니까? (1. 기본 퀴즈 게임, 2. 보너스 퀴즈 게임): ", 1, 2)
        if game_type == 1:
            quiz_game = QuizGame.init_quiz()
        else:
            quiz_game = BonusQuizGame.init_quiz()

        while True:
            menu = quiz_game.choice_menu()
            if menu == 1:
                quiz_game.start()
            elif menu == 2:
                quiz_game.add_quiz()
            elif menu == 3:
                quiz_game.list_quizzes()
            elif menu == 4:
                quiz_game.get_score()
            elif menu == 5:
                break
            elif menu == 6:
                quiz_game.remove_quiz()
    except (KeyboardInterrupt, EOFError):
        OutputUtils.print_lines("", "⚠️ 입력이 중단되어 프로그램을 종료합니다.")
    finally:
        OutputUtils.print_lines("", "프로그램을 종료합니다.")
        if quiz_game:
            quiz_game.close()


        