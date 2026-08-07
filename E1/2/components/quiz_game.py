import json
from datetime import datetime
from pathlib import Path
from components.quiz import Quiz
from utils.input_utils import InputUtils
from utils.output_utils import OutputUtils

class QuizGame:
    current_dir = Path(__file__).resolve().parent
    file_path = current_dir.parent / 'state.json'

    _fallback_quizzes = [
        Quiz(
            "LIFO(Last-In, First-Out) 특징을 가지는 자료구조는 무엇인가?",
            ["큐 (Queue)", "스택 (Stack)", "트리 (Tree)", "그래프 (Graph)"],
            1,
            {
                "sentence": "입력된 순서의 반대로 출력되는 후입선출 자료구조입니다.",
                "cost": 100
            }
        ),
        Quiz(
            "OSI 7계층 중 IP 주소를 기반으로 패킷의 경로를 결정하는 3계층(네트워크 계층)의 주요 장비는?",
            ["스위치 (Switch)", "라우터 (Router)", "리피터 (Repeater)", "허브 (Hub)"],
            1,
            {
                "sentence": "데이터 전송 최적의 경로를 지정해주는 장비입니다.",
                "cost": 100
            }
        ),
        Quiz(
            "데이터베이스 트랜잭션의 안전성을 보장하기 위한 ACID 특성에 포함되지 않는 것은?",
            ["원자성 (Atomicity)", "일관성 (Consistency)", "보안성 (Security)", "고립성 (Isolation)"],
            2,
            {
                "sentence": "보안성(Security)은 독립적인 대분류 보안 영역에 속합니다.",
                "cost": 100
            }
        ),
        Quiz(
            "두 개 이상의 프로세스가 서로 자원을 점유한 상태에서 상대방의 자원을 요구하며 무한히 대기하는 현상은?",
            ["교착 상태 (Deadlock)", "문맥 교환 (Context Switching)",
             "인터럽트 (Interrupt)", "임계 구역 (Critical Section)"],
            0,
            {
                "sentence": "영문으로 Deadlock이라 불리는 교착 현상입니다.",
                "cost": 100
            }
        ),
        Quiz(
            "최악의 경우(Worst-case)에도 O(n log n)의 시간 복잡도를 보장하는 정렬 알고리즘은?",
            ["버블 정렬 (Bubble Sort)", "선택 정렬 (Selection Sort)",
             "삽입 정렬 (Insertion Sort)", "병합 정렬 (Merge Sort)"],
            3,
            {
                "sentence": "분할 정복(Divide and Conquer) 방식을 사용하는 정렬입니다.",
                "cost": 100
            }
        )
    ]
    
    def __init__(self, quizzes, best_state, game_histories, is_loaded):
        self.quizzes = quizzes
        self.best_state = best_state
        self.game_histories = game_histories
        self.is_loaded = is_loaded

    # 기존에 저장된 퀴즈가 있다면 불러옴
    # 없거나 손상되었으면 새로 시작 및 복구
    @staticmethod
    def init_quiz():
        quizzes = []
        try:
            with open(QuizGame.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                raise TypeError("JSON 최상위 데이터가 딕셔너리 구조가 아닙니다.")
                
            quiz_list = data.get('quizzes')
            if not isinstance(quiz_list, list):
                raise TypeError("'quizzes' 데이터가 리스트 구조가 아닙니다.")

            for quiz_data in quiz_list:
                quizzes.append(Quiz(
                    quiz_data['question'],
                    quiz_data['choices'],
                    quiz_data['answer'],
                    quiz_data.get('hint_data')
                ))

            best_state = data.get('bestState', {"score": 0, "correct": 0, "total": len(quizzes)})
            game_histories = data.get('gameHistories', [])
            return QuizGame(quizzes, best_state, game_histories, True)

        except FileNotFoundError:
            print("데이터 파일이 없습니다. 기본 퀴즈 데이터로 시작합니다.")
            return QuizGame._save_default_state()

        except (TypeError, ValueError, json.JSONDecodeError, KeyError) as error:
            print(f"⚠️ 데이터 형식이 잘못되었거나 파일이 손상되었습니다. 기본 데이터로 복구합니다. {error}")
            return QuizGame._save_default_state()

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
            
            user_answer = InputUtils.get_valid_int("정답 입력: ", 1, 4)

            result_str = "✅ 정답입니다!" if quiz.is_correct(user_answer) else "❌ 오답입니다!"
            if quiz.is_correct(user_answer):
                correct_answer_count += 1
            OutputUtils.print_lines(result_str, "----------------------------------------")

        total_score = int(correct_answer_count / total_question_count * 100)
        
        is_new_record = total_score > self.best_state["score"]
        if is_new_record:
            self.best_state["score"] = total_score
            self.best_state["correct"] = correct_answer_count
            self.best_state["total"] = total_question_count
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
        hint_sentence = input("힌트 문구 (선택사항, 없으면 Enter): ").strip()
        hint_data = {"sentence": hint_sentence, "cost": 100} if hint_sentence else None

        self.quizzes.append(Quiz(question, choices, answer - 1, hint_data))
        self.save_current_state()
        OutputUtils.print_lines("✅ 퀴즈가 추가되었습니다!", "", "")

    def list_quizzes(self):
        if not self.quizzes:
            OutputUtils.print_lines("", "📋 등록된 퀴즈가 없습니다.", "")
            return
        items = [f"[{idx + 1}] {quiz.get_question()}" for idx, quiz in enumerate(self.quizzes)]
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

    @staticmethod
    def _save_default_state():
        """기본 퀴즈 데이터를 state.json 파일에 복구/초기화하여 저장합니다."""
        default_data = {
            "quizzes": [
                {
                    "question": q.question,
                    "choices": q.choices,
                    "answer": q.answer,
                    "hint_data": q.hint_data
                }
                for q in QuizGame._fallback_quizzes
            ],
            "bestState": {
                "score": 0,
                "correct": 0,
                "total": len(QuizGame._fallback_quizzes)
            },
            "gameHistories": []
        }
        try:
            with open(QuizGame.file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=4)
        except (OSError, TypeError) as e:
            print(f"⚠️ 기본 데이터 파일 저장 실패: {e}")
        
        return QuizGame(QuizGame._fallback_quizzes, {"score": 0, "correct": 0, "total": len(QuizGame._fallback_quizzes)}, [], False)

    def save_current_state(self):
        save_data = {
            "quizzes": [
                {
                    "question": q.question,
                    "choices": q.choices,
                    "answer": q.answer,
                    "hint_data": q.hint_data
                }
                for q in self.quizzes
            ],
            "bestState": self.best_state,
            "gameHistories": self.game_histories
        }
        try:
            with open(QuizGame.file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
            print("데이터가 성공적으로 저장되었습니다.")
        except (OSError, TypeError) as e:
            print(f"⚠️ 데이터 저장 실패: {e}")

    def update_game_histories(self, score):
        self.game_histories.append(score)
