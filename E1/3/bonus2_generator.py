import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from main import Utils


def generate_cross_pattern(n):
    matrix = [[0.0] * n for _ in range(n)]
    center = n // 2
    for i in range(n):
        matrix[center][i] = 1.0
        matrix[i][center] = 1.0
    return matrix


def generate_x_pattern(n):
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        matrix[i][i] = 1.0
        matrix[i][n - 1 - i] = 1.0
    return matrix


def print_pattern(matrix):
    for row in matrix:
        print(' '.join(str(int(v)) for v in row))


def demo_pattern_generator(n):
    print(f"\n--- N={n} Cross 패턴 (자동 생성) ---")
    cross = generate_cross_pattern(n)
    print_pattern(cross)

    print(f"\n--- N={n} X 패턴 (자동 생성) ---")
    x = generate_x_pattern(n)
    print_pattern(x)
    return cross, x


def run_generated_judgement(n, cross, x, pattern_label):
    pattern = generate_cross_pattern(n) if pattern_label == "cross" else generate_x_pattern(n)
    cross_score = Utils.calculate_mac(cross, pattern)
    x_score = Utils.calculate_mac(x, pattern)
    verdict = Utils.judge(cross_score, "Cross", x_score, "X")

    print(f"\n--- 생성된 {pattern_label} 패턴으로 판정 (모드1 재활용 예시) ---")
    print(f"Cross 점수: {cross_score}")
    print(f"X 점수: {x_score}")
    print(f"판정: {verdict}")


if __name__ == "__main__":
    print("=== 보너스2: 패턴 생성기 ===")

    while True:
        try:
            n = int(input("패턴 크기 N 입력(홀수 권장, 예: 3, 5, 13, 25): "))
            if n < 1:
                raise ValueError
            break
        except ValueError:
            print("입력 오류: 1 이상의 정수를 입력하세요.")

    cross, x = demo_pattern_generator(n)

    while True:
        choice = input("\n판정에 사용할 패턴 선택 (cross/x): ").strip().lower()
        if choice in ("cross", "x"):
            break
        print("입력 오류: cross 또는 x를 입력하세요.")

    run_generated_judgement(n, cross, x, choice)
