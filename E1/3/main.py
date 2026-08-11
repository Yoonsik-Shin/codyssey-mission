import timeit
import json
from pathlib import Path


class Utils:
    @staticmethod
    def get_cell(matrix, row, col):
        return matrix[row][col]

    @staticmethod
    def set_cell(matrix, row, col, value):
        matrix[row][col] = value

    @staticmethod
    def is_same_value(v1, v2):
        return abs(v1 - v2) < 1e-9

    @staticmethod
    def calculate_mac(filter_matrix, pattern_matrix):
        filter_sum = 0
        for f_row, p_row in zip(filter_matrix, pattern_matrix):
            for f_val, p_val in zip(f_row, p_row):
                filter_sum += f_val * p_val
        return filter_sum

    @staticmethod
    def judge(score_a, label_a, score_b, label_b):
        if Utils.is_same_value(score_a, score_b):
            return "UNDECIDED"
        return label_a if score_a > score_b else label_b

    @staticmethod
    def normalize_label(raw):
        key = str(raw).strip().lower()
        if key in ("+", "cross"):
            return "Cross"
        if key == "x":
            return "X"
        return None

    @staticmethod
    def input_matrix(n):
        matrix = [[0.0] * n for _ in range(n)]
        for row_idx in range(n):
            while True:
                tokens = input().split()
                if len(tokens) != n:
                    print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")
                    continue
                try:
                    values = [float(t) for t in tokens]
                except ValueError:
                    print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")
                    continue
                break
            for col_idx, value in enumerate(values):
                Utils.set_cell(matrix, row_idx, col_idx, value)
        return matrix


def user_input_mode():
    print("""
#----------------------------------------
# [1] 필터 입력
#----------------------------------------""")
    print("필터 A (3줄 입력, 공백 구분)")
    a_filter = Utils.input_matrix(3)
    print("✓ 필터 A 저장 완료")

    print("\n필터 B (3줄 입력, 공백 구분)")
    b_filter = Utils.input_matrix(3)
    print("✓ 필터 B 저장 완료")

    print("""
#---------------------------------------
# [2] 패턴 입력
#---------------------------------------""")
    print("패턴 (3줄 입력, 공백 구분)")
    pattern = Utils.input_matrix(3)
    print("✓ 패턴 저장 완료")

    a_score = Utils.calculate_mac(a_filter, pattern)
    b_score = Utils.calculate_mac(b_filter, pattern)
    verdict = Utils.judge(a_score, "A", b_score, "B")

    total_time_sec = timeit.timeit(
        lambda: Utils.calculate_mac(a_filter, pattern),
        number=10
    )
    avg_time_ms = (total_time_sec / 10) * 1000

    print("\n#---------------------------------------")
    print(f"# [3] MAC 결과{'' if verdict != 'UNDECIDED' else ' (판정 불가)'}")
    print("#---------------------------------------")
    print(f"A 점수: {a_score}")
    print(f"B 점수: {b_score}")
    print(f"연산 시간(평균/10회): {avg_time_ms:.3f} ms")
    if verdict == "UNDECIDED":
        print("판정: 판정 불가 (|A-B| < 1e-9)")
    else:
        print(f"판정: {verdict}")


def json_input_mode():
    print("""
#---------------------------------------
# [1] 필터 로드
#---------------------------------------""")
    current_dir = Path(__file__).resolve().parent
    file_path = current_dir / 'data.json'
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for filter_key in data['filters']:
        print(f"✓ {filter_key} 필터 로드 완료 (Cross, X)")

    print("""
#---------------------------------------
# [2] 패턴 분석 (라벨 정규화 적용)
#---------------------------------------""")
    total_count = len(data['patterns'])
    failed_cases = []

    for p_key, p_val in data['patterns'].items():
        print(f"--- {p_key} ---")

        try:
            n = int(p_key.split("_")[1])
        except (IndexError, ValueError):
            reason = f"키 형식 오류: 크기를 추출할 수 없음 ({p_key})"
            print(f"판정: FAIL ({reason})")
            failed_cases.append((p_key, reason))
            continue

        filter_group = data.get('filters', {}).get(f"size_{n}")
        if filter_group is None:
            reason = f"필터 size_{n} 없음"
            print(f"판정: FAIL ({reason})")
            failed_cases.append((p_key, reason))
            continue

        cross_filter = filter_group.get('cross')
        x_filter = filter_group.get('x')
        pattern_input = p_val.get('input')

        if cross_filter is None or x_filter is None or pattern_input is None:
            reason = f"스키마 오류: size_{n}의 cross/x 필터 또는 패턴 input 누락"
            print(f"판정: FAIL ({reason})")
            failed_cases.append((p_key, reason))
            continue

        size_mismatch = (
            len(cross_filter) != n or len(x_filter) != n or
            len(pattern_input) != n or
            any(len(row) != n for row in cross_filter) or
            any(len(row) != n for row in x_filter) or
            any(len(row) != n for row in pattern_input)
        )
        if size_mismatch:
            reason = f"크기 불일치 (필터/패턴 크기가 {n}×{n}과 다름)"
            print(f"판정: FAIL ({reason})")
            failed_cases.append((p_key, reason))
            continue

        try:
            cross_score = Utils.calculate_mac(cross_filter, pattern_input)
            x_score = Utils.calculate_mac(x_filter, pattern_input)
        except Exception as exc:
            reason = f"연산 오류: {exc}"
            print(f"판정: FAIL ({reason})")
            failed_cases.append((p_key, reason))
            continue

        verdict = Utils.judge(cross_score, "Cross", x_score, "X")
        expected_label = Utils.normalize_label(p_val.get('expected'))

        print(f"Cross 점수: {cross_score}")
        print(f"X 점수: {x_score}")

        if expected_label is None:
            result = "FAIL (expected 라벨 인식 불가)"
            failed_cases.append((p_key, f"expected 라벨 인식 불가: {p_val.get('expected')!r}"))
        elif verdict == "UNDECIDED":
            result = "FAIL (동점 규칙)"
            failed_cases.append((p_key, "동점(UNDECIDED) 처리 규칙에 따라 FAIL"))
        elif verdict == expected_label:
            result = "PASS"
        else:
            result = "FAIL (판정 불일치)"
            failed_cases.append((p_key, f"판정 불일치: 예상 {expected_label}, 실제 {verdict}"))

        print(f"판정: {verdict} | expected: {expected_label if expected_label else '알 수 없음'} | {result}")

    print("""
#---------------------------------------
# [3] 성능 분석 (평균/10회)
#---------------------------------------
크기       평균 시간(ms)    연산 횟수
-------------------------------------""")

    for n in (3, 5, 13, 25):
        try:
            filter_group = data.get('filters', {}).get(f"size_{n}")
            bench_filter = filter_group['cross']
            bench_pattern = next(
                (p_val['input'] for p_val in data['patterns'].values() if len(p_val.get('input', [])) == n),
                bench_filter
            )
        except Exception:
            bench_filter = [[1.0] * n for _ in range(n)]
            bench_pattern = [[1.0] * n for _ in range(n)]

        total_time_sec = timeit.timeit(
            lambda bf=bench_filter, bp=bench_pattern: Utils.calculate_mac(bf, bp),
            number=10
        )
        avg_time_ms = (total_time_sec / 10) * 1000
        print(f"{n}×{n}        {avg_time_ms:.3f}          {n * n}")

    print("""
#---------------------------------------
# [4] 결과 요약
#---------------------------------------""")
    print(f"총 테스트: {total_count}개")
    print(f"통과: {total_count - len(failed_cases)}개")
    print(f"실패: {len(failed_cases)}개")

    if failed_cases:
        print("\n실패 케이스:")
        for key, reason in failed_cases:
            print(f"- {key}: {reason}")


if __name__ == "__main__":
    print("=== Mini NPU Simulator ===")

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
