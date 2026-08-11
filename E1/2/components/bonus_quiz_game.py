import random
from components.quiz_game import QuizGame
from components.score_calculator import ScoreCalculator
from utils.input_utils import InputUtils
from utils.output_utils import OutputUtils

class BonusQuizGame(QuizGame):
    INIT_POINT = 1000

    def __init__(self, quizzes, best_state, game_histories, is_loaded):
        super().__init__(quizzes, best_state, game_histories, is_loaded)
        self.point = BonusQuizGame.INIT_POINT

    def choice_menu(self):
        info = f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_state['score']}점, 포인트 {self.point}P)" if self.is_loaded else f"💰 현재 포인트: {self.point}P"
        options = ["퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "종료", "퀴즈 삭제 (보너스)"]
        OutputUtils.render_menu("🎯 나만의 보너스 퀴즈 게임 🎯", options, info)
        return InputUtils.get_valid_int("선택: ", 1, len(options))

    def _use_hint(self, quiz) -> bool:
        """힌트를 조회하고 포인트를 차감하는 게임 전용 메서드"""
        if not quiz.has_hint():
            OutputUtils.print_lines("💡 이 문제에는 등록된 힌트가 없습니다.", "")
            return False

        cost = quiz.get_hint_cost()
        if self.point < cost:
            OutputUtils.print_lines(f"⚠️ 포인트가 부족합니다! (현재 보유: {self.point}P / 필요: {cost}P)", "")
            return False

        self.point -= cost
        OutputUtils.print_lines(
            "",
            f"💡 [힌트] {quiz.get_hint_sentence()}",
            f"   (포인트 -{cost}P 차감 / 남은 포인트: {self.point}P)",
            ""
        )
        return True

    # 1. 랜덤 출제 + 2. 문제 수 선택 + 3. 힌트 및 포인트 차감
    def start(self):
        if not self.quizzes:
            OutputUtils.print_lines("", "⚠️ 등록된 퀴즈가 없습니다. 퀴즈를 먼저 추가해주세요.", "")
            return

        exist_quiz_count = len(self.quizzes)
        question_count = InputUtils.get_valid_int(f"몇 개의 퀴즈를 풀까요? (1~{exist_quiz_count}): ", 1, exist_quiz_count)
        correct_answer_count = 0
        
        OutputUtils.print_lines("", f"📝 퀴즈를 시작합니다! (총 {question_count}문제 / 보유 포인트: {self.point}P)", "")

        random_order = random.sample(self.quizzes, question_count)

        for idx, quiz in enumerate(random_order):
            OutputUtils.print_lines("----------------------------------------", f"문제 {idx + 1}")
            quiz.display(show_hint_option=True)
            OutputUtils.print_lines("")

            while True:
                user_input = InputUtils.get_valid_int("정답 입력 (1-4, 힌트: 5): ", 1, 5)
                if user_input == 5:
                    self._use_hint(quiz)
                    continue
                user_answer = user_input
                break

            result_str = "✅ 정답입니다!" if quiz.is_correct(user_answer) else "❌ 오답입니다!"
            if quiz.is_correct(user_answer):
                correct_answer_count += 1
            OutputUtils.print_lines(result_str)

        # ScoreCalculator 책임 분리 적용
        total_score = ScoreCalculator.calculate_score(correct_answer_count, question_count)

        lines = [
            "----------------------------------------",
            "🎉 퀴즈 종료!",
            f"총 점수: {total_score}점 ({question_count}문제 중 {correct_answer_count}문제 정답)",
            f"남은 포인트: {self.point}P",
            "----------------------------------------"
        ]

        if ScoreCalculator.is_new_record(total_score, self.best_state["score"]):
            lines.append("✨ 신기록 달성!")
            self.best_state = ScoreCalculator.create_best_state(total_score, correct_answer_count, question_count)

        OutputUtils.print_lines(*lines)
        self.record_game_history(question_count, correct_answer_count, total_score)
        self.save_current_state()

    # 4. 퀴즈 삭제 기능 (보너스 과제)
    def remove_quiz(self):
        if not self.quizzes:
            OutputUtils.print_lines("", "⚠️ 삭제할 퀴즈가 없습니다.", "")
            return

        items = [f"[{idx + 1}] {quiz.get_question()}" for idx, quiz in enumerate(self.quizzes)]
        OutputUtils.print_lines(
            "",
            "📌 삭제할 퀴즈 번호를 선택하세요.",
            "",
            *items,
            "[0] 취소",
            "========================================"
        )
        selected_idx = InputUtils.get_valid_int(f"삭제할 번호 (0: 취소 / 1-{len(self.quizzes)}): ", 0, len(self.quizzes))
        if selected_idx == 0:
            OutputUtils.print_lines("", "↩️ 삭제를 취소했습니다.", "")
            return
        removed_quiz = self.quizzes.pop(selected_idx - 1)
        self.save_current_state()
        OutputUtils.print_lines("", f"✅ [{removed_quiz.get_question()}] 퀴즈가 삭제되었습니다!", "")
