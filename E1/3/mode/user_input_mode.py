from utils.input_utils import InputUtils
from utils.output_utils import OutputUtils
from utils.benchmark_utils import BenchmarkUtils
from mac_calculator import MacCalculator

def user_input_mode():
    print_lines = []

    OutputUtils.print_lines(
        "",
        "#----------------------------------------",
        "# [1] 필터 입력",
        "#----------------------------------------",
        "필터 A (3줄 입력, 공백 구분)"
    )
    a_filter = InputUtils.input_matrix(3)
    OutputUtils.print_lines("✓ 필터 A 저장 완료", "", "필터 B (3줄 입력, 공백 구분)")

    b_filter = InputUtils.input_matrix(3)
    OutputUtils.print_lines(
        "✓ 필터 B 저장 완료",
        "",
        "#---------------------------------------",
        "# [2] 패턴 입력",
        "#---------------------------------------",
        "패턴 (3줄 입력, 공백 구분)"
    )

    pattern = InputUtils.input_matrix(3)
    OutputUtils.print_lines("✓ 패턴 저장 완료")

    a_score = MacCalculator.calculate_2d(a_filter, pattern)
    b_score = MacCalculator.calculate_2d(b_filter, pattern)

    verdict = MacCalculator.judge(a_score, "A", b_score, "B")
    undecided = MacCalculator.is_undecided(verdict)

    avg_time_ms = BenchmarkUtils.measure_avg_ms(
        lambda: MacCalculator.calculate_2d(a_filter, pattern),
        number=10
    )

    print_lines.extend([
        "",
        "#---------------------------------------",
        f"# [3] MAC 결과{' (판정 불가)' if undecided else ''}",
        "#---------------------------------------",
        f"A 점수: {a_score}",
        f"B 점수: {b_score}",
        f"연산 시간(평균/10회): {avg_time_ms:.3f} ms",
        f"판정: 판정 불가 (|A-B| < {MacCalculator.TIE_EPSILON:g})" if undecided
            else f"판정: {verdict}"
    ])

    OutputUtils.print_lines(print_lines)
