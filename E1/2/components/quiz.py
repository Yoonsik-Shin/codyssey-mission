from utils.output_utils import OutputUtils

class Quiz:
    def __init__(self, question, choices, answer, hint_data=None, category="CS", difficulty="Normal"):
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint_data = hint_data or {}
        self.category = category
        self.difficulty = difficulty

    def display(self, show_hint_option=False):
        choices_str = [f"{i + 1}. {choice}" for i, choice in enumerate(self.choices)]
        meta_str = f"[{self.category} | 난이도: {self.difficulty}]"
        lines = [f"{meta_str} {self.question}", "", *choices_str]
        if show_hint_option:
            lines.append("5. 💡 포인트 사용해 힌트보기")
        OutputUtils.print_lines(*lines)

    def get_question(self):
        return self.question

    def is_correct(self, user_answer):
        return user_answer - 1 == self.answer

    def has_hint(self):
        return bool(self.hint_data and self.hint_data.get("sentence"))

    def get_hint_sentence(self):
        if isinstance(self.hint_data, dict):
            return self.hint_data.get("sentence")
        elif isinstance(self.hint_data, str):
            return self.hint_data
        return None

    def get_hint_cost(self):
        if isinstance(self.hint_data, dict):
            return self.hint_data.get("cost") or self.hint_data.get("point") or 100
        return 100

    def to_dict(self):
        """Quiz 객체를 딕셔너리로 직렬화합니다."""
        return {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
            "hint_data": self.hint_data,
            "category": self.category,
            "difficulty": self.difficulty
        }

    @classmethod
    def from_dict(cls, data: dict):
        """딕셔너리로부터 Quiz 객체를 생성합니다."""
        return cls(
            question=data['question'],
            choices=data['choices'],
            answer=data['answer'],
            hint_data=data.get('hint_data'),
            category=data.get('category', 'CS'),
            difficulty=data.get('difficulty', 'Normal')
        )

