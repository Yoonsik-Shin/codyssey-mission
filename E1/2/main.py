import json
from pathlib import Path

class Quiz:
    def __init__(self, question, choices, answer):
        self.question = question
        self.choices = choices
        self.answer = answer
    
    def display(self):
        print(self.question)
        print()
        for i, choice in enumerate(self.choices):
            print(f"{i+1}. {choice}")
    
    def getQuestion(self):
        return self.question

    def is_correct(self, user_answer):
        return user_answer - 1 == self.answer

class QuizGame:
    current_dir = Path(__file__).resolve().parent
    file_path = current_dir / 'state.json'

    _fallback_quizzes = [
        Quiz(
            "LIFO(Last-In, First-Out) 특징을 가지는 자료구조는 무엇인가?",
            ["큐 (Queue)", "스택 (Stack)", "트리 (Tree)", "그래프 (Graph)"],
            1
        ),
        Quiz(
            "OSI 7계층 중 IP 주소를 기반으로 패킷의 경로를 결정하는 3계층(네트워크 계층)의 주요 장비는?",
            ["스위치 (Switch)", "라우터 (Router)", "리피터 (Repeater)", "허브 (Hub)"],
            1
        ),
        Quiz(
            "데이터베이스 트랜잭션의 안전성을 보장하기 위한 ACID 특성에 포함되지 않는 것은?",
            ["원자성 (Atomicity)", "일관성 (Consistency)", "보안성 (Security)", "고립성 (Isolation)"],
            2
        ),
        Quiz(
            "두 개 이상의 프로세스가 서로 자원을 점유한 상태에서 상대방의 자원을 요구하며 무한히 대기하는 현상은?",
            ["교착 상태 (Deadlock)", "문맥 교환 (Context Switching)",
             "인터럽트 (Interrupt)", "임계 구역 (Critical Section)"],
            0
        ),
        Quiz(
            "최악의 경우(Worst-case)에도 O(n log n)의 시간 복잡도를 보장하는 정렬 알고리즘은?",
            ["버블 정렬 (Bubble Sort)", "선택 정렬 (Selection Sort)",
             "삽입 정렬 (Insertion Sort)", "병합 정렬 (Merge Sort)"],
            3
        )
    ]
    
    def __init__(self, quizzes, best_state, is_loaded):
        self.quizzes = quizzes
        self.best_state = best_state
        self.is_loaded = is_loaded
    
    @staticmethod
    def _save_default_state():
        """기본 퀴즈 데이터를 state.json 파일에 복구/초기화하여 저장합니다."""
        default_data = {
            "quizzes": [
                {
                    "question": q.question,
                    "choices": q.choices,
                    "answer": q.answer
                }
                for q in QuizGame._fallback_quizzes
            ],
            "bestState": {
                "score": 0,
                "correct": 0,
                "total": len(QuizGame._fallback_quizzes)
            }
        }
        try:
            with open(QuizGame.file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=4)
        except (OSError, TypeError) as e:
            print(f"⚠️ 기본 데이터 파일 저장 실패: {e}")

    def save_state(self):
        save_data = {
            "quizzes": [
                {
                    "question": q.question,
                    "choices": q.choices,
                    "answer": q.answer
                }
                for q in self.quizzes
            ],
            "bestState": self.best_state
        }
        try:
            with open(QuizGame.file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=4)
            print("데이터가 성공적으로 저장되었습니다.")
        except (OSError, TypeError) as e:
            print(f"⚠️ 데이터 저장 실패: {e}")

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
                    quiz_data['answer']
                ))

            best_state = data.get('bestState', {"score": 0, "correct": 0, "total": len(quizzes)})
            return QuizGame(quizzes, best_state, True)

        except FileNotFoundError:
            print("데이터 파일이 없습니다. 기본 퀴즈 데이터로 시작합니다.")
            QuizGame._save_default_state()
            return QuizGame(QuizGame._fallback_quizzes, {"score": 0, "correct": 0, "total": len(QuizGame._fallback_quizzes)}, False)
        except (TypeError, ValueError, json.JSONDecodeError, KeyError) as error:
            print(f"⚠️ 데이터 형식이 잘못되었거나 파일이 손상되었습니다. 기본 데이터로 복구합니다. {error}")
            QuizGame._save_default_state()
            return QuizGame(QuizGame._fallback_quizzes, {"score": 0, "correct": 0, "total": len(QuizGame._fallback_quizzes)}, False)

    def choice_menu(self):
        while True:
            print("========================================")
            print("     🎯 나만의 퀴즈 게임 🎯")
            print("========================================")
            if self.is_loaded:
                print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(self.quizzes)}개, 최고점수 {self.best_state['score']}점)")
                print("========================================")
            print("1. 퀴즈 풀기")
            print("2. 퀴즈 추가")
            print("3. 퀴즈 목록")
            print("4. 점수 확인")
            print("5. 종료")
            print("========================================")
            try:
                choice = int(input("선택: ").strip())
                if not (1 <= choice <= 5):
                    print("⚠️ 잘못된 입력입니다. 1-5 사이의 숫자를 입력하세요.")
                    continue
                break
            except ValueError:
                print("⚠️ 잘못된 입력입니다. 1-5 사이의 숫자를 입력하세요.")
        return choice

    def start(self):
        if not self.quizzes:
            print("\n⚠️ 등록된 퀴즈가 없습니다. 퀴즈를 먼저 추가해주세요.\n")
            return

        total_question_count = len(self.quizzes)
        correct_answer_count = 0
        
        print()
        print(f"📝 퀴즈를 시작합니다! (총 {total_question_count}문제)")
        print()

        for idx, quiz in enumerate(self.quizzes):
            print("----------------------------------------")
            print(f"문제 {idx + 1}")
            quiz.display()
            print()
            
            while True:
                try:
                    user_answer = int(input("정답 입력: ").strip())
                except ValueError:
                    print("⚠️ 잘못된 입력입니다. 1-4 사이의 숫자를 입력하세요.")
                    continue

                if not (1 <= user_answer <= 4):
                    print("⚠️ 잘못된 입력입니다. 1-4 사이의 숫자를 입력하세요.")
                    continue
                break

            if quiz.is_correct(user_answer):
                print("✅ 정답입니다!")
                correct_answer_count += 1
                print()
            else:
                print("❌ 오답입니다!")
            print("----------------------------------------")

        total_score = int(correct_answer_count / total_question_count * 100)
        
        print() 
        print("========================================")
        print(f"🏆 결과: {correct_answer_count}문제 중 {total_question_count}문제 정답! ({total_score}점)")
        if (total_score > self.best_state["score"]):
            print("🎉 새로운 최고 점수입니다!")
            self.best_state["score"] = total_score
            self.best_state["correct"] = correct_answer_count
            self.best_state["total"] = total_question_count
        else:
            print(f"아쉬워요! 최고 점수: {self.best_state['score']}점")
        print("========================================")
        self.save_state()

    def add_quiz(self):
        print()
        print("📌 새로운 퀴즈를 추가합니다.")
        question = input("문제를 입력하세요: ").strip()            
        choices = []
        for i in range(4):
            choices.append(input(f"선택지 {i + 1}:").strip())
        while True:
            try:
                answer = int(input("정답 번호 (1-4):").strip())
                if not (1 <= answer <= 4):
                    raise ValueError("잘못된 입력입니다. 1-4 사이의 숫자를 입력하세요.")
                break
            except ValueError as e:
                print(f"⚠️ {e}")
        self.quizzes.append(Quiz(question, choices, answer - 1))
        print("✅ 퀴즈가 추가되었습니다!")
        print()

    def list_quizzes(self):
        if not self.quizzes:
            print("\n📋 등록된 퀴즈가 없습니다.\n")
            return
        print()
        print(f"📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print()
        for idx, quiz in enumerate(self.quizzes):
            print(f"[{idx + 1}] {quiz.getQuestion()}")
        print("========================================")
        print()

    def get_score(self):
        if self.best_state["total"] == 0:
            print("\n🏆 아직 완료한 퀴즈 기록이 없습니다.\n")
        else:
            print(f"\n🏆 최고 점수: {self.best_state['score']}점 ({self.best_state['total']}문제 중 {self.best_state['correct']}문제 정답)\n")
    
    def close(self):
        self.save_state()

if __name__ == "__main__":
    quiz_game = None
    try:
        quiz_game = QuizGame.init_quiz()
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
    except (KeyboardInterrupt, EOFError):
        print("\n입력이 중단되어 프로그램을 종료합니다.")
    finally:
        print("\n프로그램을 종료합니다.")
        if quiz_game:
            quiz_game.close()

        