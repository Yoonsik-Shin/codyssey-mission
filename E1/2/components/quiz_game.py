import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from components.quiz import Quiz
from components.score_calculator import ScoreCalculator
from utils.input_utils import InputUtils
from utils.output_utils import OutputUtils
from utils.logger import GameLogger

class QuizGame:
    SCHEMA_VERSION = "1.0.0"
    current_dir = Path(__file__).resolve().parent
    file_path = current_dir.parent / 'state.json'
    temp_file_path = current_dir.parent / 'state.json.tmp'
    backup_file_path = current_dir.parent / 'state.json.bak'

    _fallback_quizzes = [
        Quiz(
            "LIFO(Last-In, First-Out) 특징을 가지는 자료구조는 무엇인가?",
            ["큐 (Queue)", "스택 (Stack)", "트리 (Tree)", "그래프 (Graph)"],
            1,
            {
                "sentence": "입력된 순서의 반대로 출력되는 후입선출 자료구조입니다.",
                "cost": 100
            },
            "Data Structure",
            "Easy"
        ),
        Quiz(
            "OSI 7계층 중 IP 주소를 기반으로 패킷의 경로를 결정하는 3계층(네트워크 계층)의 주요 장비는?",
            ["스위치 (Switch)", "라우터 (Router)", "리피터 (Repeater)", "허브 (Hub)"],
            1,
            {
                "sentence": "데이터 전송 최적의 경로를 지정해주는 장비입니다.",
                "cost": 100
            },
            "Network",
            "Medium"
        ),
        Quiz(
            "데이터베이스 트랜잭션의 안전성을 보장하기 위한 ACID 특성에 포함되지 않는 것은?",
            ["원자성 (Atomicity)", "일관성 (Consistency)", "보안성 (Security)", "고립성 (Isolation)"],
            2,
            {
                "sentence": "보안성(Security)은 독립적인 대분류 보안 영역에 속합니다.",
                "cost": 100
            },
            "Database",
            "Medium"
        ),
        Quiz(
            "두 개 이상의 프로세스가 서로 자원을 점유한 상태에서 상대방의 자원을 요구하며 무한히 대기하는 현상은?",
            ["교착 상태 (Deadlock)", "문맥 교환 (Context Switching)",
             "인터럽트 (Interrupt)", "임계 구역 (Critical Section)"],
            0,
            {
                "sentence": "영문으로 Deadlock이라 불리는 교착 현상입니다.",
                "cost": 100
            },
            "OS",
            "Medium"
        ),
        Quiz(
            "최악의 경우(Worst-case)에도 O(n log n)의 시간 복잡도를 보장하는 정렬 알고리즘은?",
            ["버블 정렬 (Bubble Sort)", "선택 정렬 (Selection Sort)",
             "삽입 정렬 (Insertion Sort)", "병합 정렬 (Merge Sort)"],
            3,
            {
                "sentence": "분할 정복(Divide and Conquer) 방식을 사용하는 정렬입니다.",
                "cost": 100
            },
            "Algorithm",
            "Hard"
        )
    ]
    
    def __init__(self, quizzes, best_state, game_histories, is_loaded):
        self.quizzes = quizzes
        self.best_state = best_state
        self.game_histories = game_histories
        self.is_loaded = is_loaded

    @classmethod
    def init_quiz(cls):
        """저장된 퀴즈 상태를 불러옵니다. 주 파일 손상 시 백업 파일 또는 기본 데이터로 복구합니다."""
        if QuizGame.file_path.exists():
            game_inst = cls._load_from_path(QuizGame.file_path)
            if game_inst:
                return game_inst

        # 백업 파일에서 복구 시도
        if QuizGame.backup_file_path.exists():
            print("⚠️ 메인 데이터 파일이 손상되었거나 없습니다. 백업 파일(.bak)에서 복구를 시도합니다.")
            game_inst = cls._load_from_path(QuizGame.backup_file_path)
            if game_inst:
                game_inst.save_current_state()
                return game_inst

        print("⚠️ 백업 데이터가 없거나 손상되었습니다. 기본 퀴즈 데이터로 복구/초기화합니다.")
        return cls._save_default_state()

    @classmethod
    def _load_from_path(cls, path: Path):
        quizzes = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                raise TypeError("JSON 최상위 데이터가 딕셔너리 구조가 아닙니다.")
                
            quiz_list = data.get('quizzes')
            if not isinstance(quiz_list, list):
                raise TypeError("'quizzes' 데이터가 리스트 구조가 아닙니다.")

            for quiz_data in quiz_list:
                quizzes.append(Quiz.from_dict(quiz_data))

            best_state = data.get('bestState', {"score": 0, "correct": 0, "total": len(quizzes)})
            game_histories = data.get('gameHistories', [])
            return cls(quizzes, best_state, game_histories, True)

        except (TypeError, ValueError, json.JSONDecodeError, KeyError, OSError) as error:
            GameLogger.log_error(f"파일 경로({path}) 파싱 및 불어오기 실패", error)
            return None

    def choice_menu(self):
        info = f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_state['score']}점)" if self.is_loaded else None
        options = ["퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "종료"]
        OutputUtils.render_menu("🎯 나만의 퀴즈 게임 🎯", options, info)
        return InputUtils.get_valid_int("선택: ", 1, len(options))

    def record_game_history(self, total_question_count, correct_answer_count, total_score):
        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_quiz_count": total_question_count,
            "correct_quiz_count": correct_answer_count,
            "score": total_score
        }
        self.game_histories.append(history_entry)

    def start(self):
        if not self.quizzes:
            OutputUtils.print_lines("", "⚠️ 등록된 퀴즈가 없습니다. 퀴즈를 먼저 추가해주세요.", "")
            return

        total_question_count = len(self.quizzes)
        correct_answer_count = 0
        
        OutputUtils.print_lines("", f"📝 퀴즈를 시작합니다! (총 {total_question_count}문제)", "")

        for idx, quiz in enumerate(self.quizzes):
            OutputUtils.print_lines("----------------------------------------", f"문제 {idx + 1}")
            quiz.display()
            OutputUtils.print_lines("")
            
            user_answer = InputUtils.get_valid_int("정답 입력 (1-4): ", 1, 4)

            result_str = "✅ 정답입니다!" if quiz.is_correct(user_answer) else "❌ 오답입니다!"
            if quiz.is_correct(user_answer):
                correct_answer_count += 1
            OutputUtils.print_lines(result_str, "----------------------------------------")

        # ScoreCalculator 책임 분리 적용
        total_score = ScoreCalculator.calculate_score(correct_answer_count, total_question_count)
        
        is_new_record = ScoreCalculator.is_new_record(total_score, self.best_state["score"])
        if is_new_record:
            self.best_state = ScoreCalculator.create_best_state(total_score, correct_answer_count, total_question_count)
            record_msg = "🎉 새로운 최고 점수입니다!"
        else:
            record_msg = f"아쉬워요! 최고 점수: {self.best_state['score']}점"

        OutputUtils.print_lines(
            "",
            "========================================",
            f"🏆 결과: {correct_answer_count}문제 중 {total_question_count}문제 정답! ({total_score}점)",
            record_msg,
            "========================================"
        )
        self.record_game_history(total_question_count, correct_answer_count, total_score)
        self.save_current_state()

    def add_quiz(self):
        OutputUtils.print_lines("", "📌 새로운 퀴즈를 추가합니다.")
        question = InputUtils.get_non_empty_string("문제를 입력하세요: ", "⚠️ 문제는 빈 값일 수 없습니다. 다시 입력해 주세요.")
        choices = [
            InputUtils.get_non_empty_string(f"선택지 {i + 1}: ", "⚠️ 선택지는 빈 값일 수 없습니다. 다시 입력해 주세요.")
            for i in range(4)
        ]
        answer = InputUtils.get_valid_int("정답 번호 (1-4): ", 1, 4)
        category = input("카테고리 (기본값 CS): ").strip() or "CS"
        difficulty = input("난이도 (Easy/Normal/Hard, 기본값 Normal): ").strip() or "Normal"
        hint_sentence = input("힌트 문구 (선택사항, 없으면 Enter): ").strip()
        hint_data = {"sentence": hint_sentence, "cost": 100} if hint_sentence else None

        self.quizzes.append(Quiz(question, choices, answer - 1, hint_data, category, difficulty))
        self.save_current_state()
        OutputUtils.print_lines("✅ 퀴즈가 추가되었습니다!", "", "")

    def list_quizzes(self):
        if not self.quizzes:
            OutputUtils.print_lines("", "📋 등록된 퀴즈가 없습니다.", "")
            return
        items = [f"[{idx + 1}] [{quiz.category} | {quiz.difficulty}] {quiz.get_question()}" for idx, quiz in enumerate(self.quizzes)]
        OutputUtils.print_lines(
            "",
            f"📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)",
            "",
            *items,
            "========================================",
            ""
        )

    def get_score(self):
        lines = []
        if self.best_state["total"] == 0:
            lines.append("🏆 아직 완료한 퀴즈 기록이 없습니다.")
        else:
            lines.append(f"🏆 최고 점수: {self.best_state['score']}점 ({self.best_state['total']}문제 중 {self.best_state['correct']}문제 정답)")

        if self.game_histories:
            lines.extend(["", "📜 [ 최근 게임 기록 히스토리 ]"])
            recent_histories = self.game_histories[-5:]
            for idx, h in enumerate(reversed(recent_histories)):
                timestamp = h.get("timestamp", "일시 정보 없음")
                total = h.get("total_quiz_count", 0)
                correct = h.get("correct_quiz_count", 0)
                score = h.get("score", 0)
                lines.append(f"  • [{idx + 1}] {timestamp} | 정답: {correct}/{total}문제 ({score}점)")

        OutputUtils.print_lines("", *lines, "")

    def close(self):
        self.save_current_state()

    @classmethod
    def _save_default_state(cls):
        """기본 퀴즈 데이터를 state.json 파일에 복구/초기화하여 저장합니다."""
        default_data = {
            "schemaVersion": cls.SCHEMA_VERSION,
            "quizzes": [q.to_dict() for q in QuizGame._fallback_quizzes],
            "bestState": {
                "score": 0,
                "correct": 0,
                "total": len(QuizGame._fallback_quizzes)
            },
            "gameHistories": []
        }
        cls._atomic_write(QuizGame.file_path, default_data)
        cls._create_backup()
        return cls(QuizGame._fallback_quizzes, {"score": 0, "correct": 0, "total": len(QuizGame._fallback_quizzes)}, [], False)

    def save_current_state(self):
        """임시 파일 교체(Atomic write) 방식으로 안전하게 현재 게임 상태를 영속 저장합니다."""
        save_data = {
            "schemaVersion": self.SCHEMA_VERSION,
            "quizzes": [q.to_dict() for q in self.quizzes],
            "bestState": self.best_state,
            "gameHistories": self.game_histories
        }
        if self._atomic_write(QuizGame.file_path, save_data):
            self._create_backup()

    @classmethod
    def _atomic_write(cls, target_path: Path, data: dict) -> bool:
        """임시 파일 쓰기 후 원자적 교체(os.replace)로 파일 쓰기 동시성 및 손상을 방지합니다."""
        try:
            with open(cls.temp_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.flush()
                os.fsync(f.fileno())
            os.replace(cls.temp_file_path, target_path)
            return True
        except (OSError, TypeError, json.JSONDecodeError) as e:
            GameLogger.log_error(f"데이터 원자적 저장 실패 (대상: {target_path})", e)
            if cls.temp_file_path.exists():
                try:
                    cls.temp_file_path.unlink()
                except OSError:
                    pass
            print(f"⚠️ 데이터 저장 중 오류가 발생했습니다: {e}")
            return False

    @classmethod
    def _create_backup(cls):
        """state.json의 백업 스냅샷(.bak)을 생성합니다."""
        try:
            if cls.file_path.exists():
                shutil.copy2(cls.file_path, cls.backup_file_path)
        except OSError as e:
            GameLogger.log_error("백업 파일 생성 실패", e)

    def update_game_histories(self, score):
        self.game_histories.append(score)
