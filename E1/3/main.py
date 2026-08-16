
from mode.json_input_mode import json_input_mode
from mode.user_input_mode import user_input_mode

if __name__ == "__main__":
    while True:
        try:
            mode_num = int(input("[모드 선택]\n\n1. 사용자 입력 (3x3)\n2. data.json 분석\n"))
        except ValueError:
            print("입력 오류: 1 또는 2를 입력하세요.\n")
            continue
        if mode_num in (1, 2):
            break
        print("입력 오류: 1 또는 2를 입력하세요.\n")

    print(f"선택: {mode_num}")

    if mode_num == 1:
        user_input_mode()
    else:
        json_input_mode()