import sys
import os
import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from components.quiz import Quiz
from components.quiz_game import QuizGame
from components.bonus_quiz_game import BonusQuizGame
from components.score_calculator import ScoreCalculator
from utils.input_utils import InputUtils


# ──────────────────────────────────────────────
# Quiz 모델 테스트
# ──────────────────────────────────────────────
class TestQuiz(unittest.TestCase):

    def setUp(self):
        self.quiz = Quiz(
            question="LIFO 특징을 가지는 자료구조는?",
            choices=["큐", "스택", "트리", "그래프"],
            answer=1,  # 0-indexed: "스택"
            hint_data={"sentence": "후입선출 자료구조입니다.", "cost": 100},
            category="Data Structure",
            difficulty="Easy"
        )

    def test_is_correct_정답(self):
        self.assertTrue(self.quiz.is_correct(2))  # 사용자 입력 2 → 0-indexed 1 → 정답

    def test_is_correct_오답(self):
        self.assertFalse(self.quiz.is_correct(1))
        self.assertFalse(self.quiz.is_correct(3))
        self.assertFalse(self.quiz.is_correct(4))

    def test_has_hint_있음(self):
        self.assertTrue(self.quiz.has_hint())

    def test_has_hint_없음(self):
        quiz_no_hint = Quiz("질문", ["a", "b", "c", "d"], 0)
        self.assertFalse(quiz_no_hint.has_hint())

    def test_get_hint_sentence(self):
        self.assertEqual(self.quiz.get_hint_sentence(), "후입선출 자료구조입니다.")

    def test_get_hint_cost_기본값(self):
        self.assertEqual(self.quiz.get_hint_cost(), 100)

    def test_get_hint_cost_hint_없을때_기본값(self):
        quiz_no_hint = Quiz("질문", ["a", "b", "c", "d"], 0)
        self.assertEqual(quiz_no_hint.get_hint_cost(), 100)

    def test_to_dict_직렬화(self):
        d = self.quiz.to_dict()
        self.assertEqual(d["question"], "LIFO 특징을 가지는 자료구조는?")
        self.assertEqual(d["answer"], 1)
        self.assertEqual(d["category"], "Data Structure")
        self.assertIn("hint_data", d)

    def test_from_dict_역직렬화(self):
        d = self.quiz.to_dict()
        restored = Quiz.from_dict(d)
        self.assertEqual(restored.question, self.quiz.question)
        self.assertEqual(restored.answer, self.quiz.answer)
        self.assertEqual(restored.category, self.quiz.category)

    def test_from_dict_역직렬화_왕복_일치(self):
        """to_dict → from_dict 왕복 후 동일한 데이터를 유지해야 한다."""
        restored = Quiz.from_dict(self.quiz.to_dict())
        self.assertEqual(restored.to_dict(), self.quiz.to_dict())

    def test_get_question(self):
        self.assertEqual(self.quiz.get_question(), "LIFO 특징을 가지는 자료구조는?")


# ──────────────────────────────────────────────
# ScoreCalculator 테스트
# ──────────────────────────────────────────────
class TestScoreCalculator(unittest.TestCase):

    def test_calculate_score_만점(self):
        self.assertEqual(ScoreCalculator.calculate_score(5, 5), 100)

    def test_calculate_score_0점(self):
        self.assertEqual(ScoreCalculator.calculate_score(0, 5), 0)

    def test_calculate_score_부분점수(self):
        self.assertEqual(ScoreCalculator.calculate_score(3, 5), 60)

    def test_calculate_score_전체0문제_예외처리(self):
        self.assertEqual(ScoreCalculator.calculate_score(0, 0), 0)

    def test_is_new_record_갱신(self):
        self.assertTrue(ScoreCalculator.is_new_record(90, 80))

    def test_is_new_record_동점은_갱신_아님(self):
        self.assertFalse(ScoreCalculator.is_new_record(80, 80))

    def test_is_new_record_낮은점수(self):
        self.assertFalse(ScoreCalculator.is_new_record(70, 80))

    def test_create_best_state(self):
        state = ScoreCalculator.create_best_state(100, 5, 5)
        self.assertEqual(state, {"score": 100, "correct": 5, "total": 5})


# ──────────────────────────────────────────────
# QuizGame 테스트
# ──────────────────────────────────────────────
class TestQuizGame(unittest.TestCase):

    def _make_game(self, quiz_count=3):
        quizzes = [
            Quiz(f"질문{i}", ["a", "b", "c", "d"], 0)
            for i in range(quiz_count)
        ]
        best_state = {"score": 0, "correct": 0, "total": quiz_count}
        return QuizGame(quizzes, best_state, [], False)

    def test_초기화(self):
        game = self._make_game(3)
        self.assertEqual(len(game.quizzes), 3)
        self.assertFalse(game.is_loaded)

    def test_record_game_history_추가(self):
        game = self._make_game()
        game.record_game_history(5, 3, 60)
        self.assertEqual(len(game.game_histories), 1)
        self.assertEqual(game.game_histories[0]["score"], 60)
        self.assertEqual(game.game_histories[0]["correct_quiz_count"], 3)

    @patch("components.quiz_game.QuizGame._atomic_write", return_value=True)
    @patch("components.quiz_game.QuizGame._create_backup")
    def test_save_current_state_호출(self, mock_backup, mock_write):
        game = self._make_game()
        game.save_current_state()
        mock_write.assert_called_once()
        mock_backup.assert_called_once()

    @patch("components.quiz_game.QuizGame._atomic_write", return_value=False)
    @patch("components.quiz_game.QuizGame._create_backup")
    def test_save_current_state_쓰기실패시_백업안함(self, mock_backup, mock_write):
        game = self._make_game()
        game.save_current_state()
        mock_backup.assert_not_called()

    def test_add_quiz_퀴즈추가(self):
        game = self._make_game(2)
        new_quiz = Quiz("새 질문", ["a", "b", "c", "d"], 0)
        with patch.object(game, "save_current_state"):
            game.quizzes.append(new_quiz)
        self.assertEqual(len(game.quizzes), 3)

    @patch("components.quiz_game.QuizGame.file_path", new_callable=lambda: property(lambda self: Path("/nonexistent/state.json")))
    def test_load_from_path_없는파일(self, _):
        result = QuizGame._load_from_path(Path("/nonexistent/state.json"))
        self.assertIsNone(result)

    def test_load_from_path_정상(self):
        """유효한 JSON 데이터를 로드하면 QuizGame 인스턴스를 반환한다."""
        sample_data = {
            "quizzes": [
                {
                    "question": "테스트 질문",
                    "choices": ["a", "b", "c", "d"],
                    "answer": 0,
                    "hint_data": None,
                    "category": "CS",
                    "difficulty": "Normal"
                }
            ],
            "bestState": {"score": 50, "correct": 1, "total": 2},
            "gameHistories": []
        }
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(sample_data, f, ensure_ascii=False)
            tmp_path = Path(f.name)
        try:
            game = QuizGame._load_from_path(tmp_path)
            self.assertIsNotNone(game)
            self.assertEqual(len(game.quizzes), 1)
            self.assertEqual(game.best_state["score"], 50)
        finally:
            tmp_path.unlink()

    def test_load_from_path_손상된JSON(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            f.write("{ invalid json }")
            tmp_path = Path(f.name)
        try:
            result = QuizGame._load_from_path(tmp_path)
            self.assertIsNone(result)
        finally:
            tmp_path.unlink()


# ──────────────────────────────────────────────
# BonusQuizGame 테스트
# ──────────────────────────────────────────────
class TestBonusQuizGame(unittest.TestCase):

    def _make_bonus_game(self):
        quizzes = [
            Quiz(f"질문{i}", ["a", "b", "c", "d"], 0,
                 {"sentence": f"힌트{i}", "cost": 100})
            for i in range(3)
        ]
        best_state = {"score": 0, "correct": 0, "total": 3}
        return BonusQuizGame(quizzes, best_state, [], False)

    def test_초기포인트(self):
        game = self._make_bonus_game()
        self.assertEqual(game.point, BonusQuizGame.INIT_POINT)

    def test_use_hint_포인트차감(self):
        game = self._make_bonus_game()
        initial_point = game.point
        quiz = game.quizzes[0]
        with patch("components.bonus_quiz_game.OutputUtils.print_lines"):
            game._use_hint(quiz)
        self.assertEqual(game.point, initial_point - quiz.get_hint_cost())

    def test_use_hint_포인트부족(self):
        game = self._make_bonus_game()
        game.point = 50  # cost(100)보다 낮게 설정
        quiz = game.quizzes[0]
        with patch("components.bonus_quiz_game.OutputUtils.print_lines"):
            result = game._use_hint(quiz)
        self.assertFalse(result)
        self.assertEqual(game.point, 50)  # 차감 안 됨

    def test_use_hint_없는경우(self):
        game = self._make_bonus_game()
        quiz_no_hint = Quiz("힌트없는 질문", ["a", "b", "c", "d"], 0)
        with patch("components.bonus_quiz_game.OutputUtils.print_lines"):
            result = game._use_hint(quiz_no_hint)
        self.assertFalse(result)

    def test_remove_quiz_삭제(self):
        game = self._make_bonus_game()
        original_count = len(game.quizzes)
        target_question = game.quizzes[0].get_question()
        with patch.object(game, "save_current_state"):
            with patch("components.bonus_quiz_game.OutputUtils.print_lines"):
                with patch("components.bonus_quiz_game.InputUtils.get_valid_int", return_value=1):
                    game.remove_quiz()
        self.assertEqual(len(game.quizzes), original_count - 1)
        self.assertNotEqual(game.quizzes[0].get_question(), target_question)

    def test_remove_quiz_취소(self):
        game = self._make_bonus_game()
        original_count = len(game.quizzes)
        with patch.object(game, "save_current_state") as mock_save:
            with patch("components.bonus_quiz_game.OutputUtils.print_lines"):
                with patch("components.bonus_quiz_game.InputUtils.get_valid_int", return_value=0):
                    game.remove_quiz()
        self.assertEqual(len(game.quizzes), original_count)  # 변화 없음
        mock_save.assert_not_called()  # 저장 안 됨

    def test_퀴즈없을때_remove_quiz(self):
        game = BonusQuizGame([], {"score": 0, "correct": 0, "total": 0}, [], False)
        with patch("components.bonus_quiz_game.OutputUtils.print_lines"):
            game.remove_quiz()  # 예외 없이 조기 반환


# ──────────────────────────────────────────────
# InputUtils 테스트
# ──────────────────────────────────────────────
class TestInputUtils(unittest.TestCase):

    @patch("builtins.input", side_effect=["3"])
    def test_get_valid_int_정상(self, _):
        result = InputUtils.get_valid_int("입력: ", 1, 5)
        self.assertEqual(result, 3)

    @patch("builtins.input", side_effect=["0", "6", "abc", "3"])
    def test_get_valid_int_범위밖후_정상(self, _):
        result = InputUtils.get_valid_int("입력: ", 1, 5)
        self.assertEqual(result, 3)

    @patch("builtins.input", side_effect=["y"])
    def test_get_confirm_yes_no_yes(self, _):
        self.assertTrue(InputUtils.get_confirm_yes_no())

    @patch("builtins.input", side_effect=["n"])
    def test_get_confirm_yes_no_no(self, _):
        self.assertFalse(InputUtils.get_confirm_yes_no())

    @patch("builtins.input", side_effect=["maybe", "y"])
    def test_get_confirm_yes_no_잘못된입력후_yes(self, _):
        self.assertTrue(InputUtils.get_confirm_yes_no())

    @patch("builtins.input", side_effect=["hello"])
    def test_get_non_empty_string(self, _):
        result = InputUtils.get_non_empty_string("입력: ")
        self.assertEqual(result, "hello")

    @patch("builtins.input", side_effect=["", "  ", "valid"])
    def test_get_non_empty_string_빈값후_정상(self, _):
        result = InputUtils.get_non_empty_string("입력: ")
        self.assertEqual(result, "valid")


if __name__ == "__main__":
    unittest.main(verbosity=2)
