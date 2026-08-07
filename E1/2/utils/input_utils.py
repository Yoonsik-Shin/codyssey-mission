class InputUtils:
    @staticmethod
    def get_valid_int(prompt: str, min_val: int, max_val: int, custom_error_msg: str = None) -> int:
        """범위 내의 정수 입력을 안전하게 받아 반환합니다."""
        default_error_msg = f"⚠️ 잘못된 입력입니다. {min_val}-{max_val} 사이의 숫자를 입력하세요."
        error_msg = custom_error_msg if custom_error_msg else default_error_msg

        while True:
            raw_input = input(prompt).strip()
            if not raw_input:
                print("⚠️ 빈 입력입니다. 숫자를 입력하세요.")
                continue

            try:
                val = int(raw_input)
                if not (min_val <= val <= max_val):
                    print(error_msg)
                    continue
                return val
            except ValueError:
                print(error_msg)

    @staticmethod
    def get_non_empty_string(prompt: str, custom_error_msg: str = None) -> str:
        """비어있지 않은 문자열 입력을 안전하게 받아 반환합니다."""
        error_msg = custom_error_msg if custom_error_msg else "⚠️ 빈 값은 입력할 수 없습니다. 다시 입력해 주세요."
        while True:
            text = input(prompt).strip()
            if not text:
                print(error_msg)
                continue
            return text
