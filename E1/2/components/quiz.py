from utils.output_utils import OutputUtils

class Quiz:
    def __init__(self, question, choices, answer, hint_data=None):
        self.question = question
        self.choices = choices
        self.answer = answer
        self.hint_data = hint_data or {}

    def display(self, show_hint_option=False):
        choices_str = [f"{i + 1}. {choice}" for i, choice in enumerate(self.choices)]
        lines = [self.question, "", *choices_str]
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
