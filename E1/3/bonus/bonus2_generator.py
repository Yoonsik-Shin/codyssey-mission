import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mac_calculator import MacCalculator
from utils.matrix_utils import MatrixUtils
from utils.output_utils import OutputUtils

if __name__ == "__main__":
    print_lines = ["=== 보너스2: 패턴 생성기 ==="]

    while True:
        try:
            n = int(input("패턴 크기 N 입력(홀수 권장, 예: 3, 5, 13, 25): "))
            if n < 1:
                raise ValueError
            break
        except ValueError:
            print("입력 오류: 1 이상의 정수를 입력하세요.")

    cross = MatrixUtils.generate_cross_pattern(n)
    x = MatrixUtils.generate_x_pattern(n)

    print_lines.extend([
        "", 
        "\n--- N={n} Cross 패턴 (자동 생성) ---", 
        MatrixUtils.print_pattern(cross), 
        "", 
        "--- N={n} X 패턴 (자동 생성) ---",
        MatrixUtils.print_pattern(x),
    ])

    while True:
        choice = input("\n판정에 사용할 패턴 선택 (cross/x): ").strip().lower()
        if choice in ("cross", "x"):
            break
        print_lines.append("입력 오류: cross 또는 x를 입력하세요.")

    pattern = MatrixUtils.generate_cross_pattern(n) if choice == "cross" else MatrixUtils.generate_x_pattern(n)
    cross_score = MacCalculator.calculate_2d(cross, pattern)
    x_score = MacCalculator.calculate_2d(x, pattern)
    verdict = MacCalculator.judge(cross_score, "Cross", x_score, "X")

    OutputUtils.print_lines(
        *print_lines,
        "",
        f"--- 생성된 {choice} 패턴으로 판정 (모드1 재활용 예시) ---",
        f"Cross 점수: {cross_score}",
        f"X 점수: {x_score}",
        f"판정: {verdict}"
    )
