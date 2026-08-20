import json
from pathlib import Path

from mac_calculator import MacCalculator
from utils.output_utils import OutputUtils
from utils.benchmark_utils import BenchmarkUtils
from label_normalizer import LabelNormalizer

def json_input_mode():
    print_lines = [
        "",
        "#---------------------------------------",
        "# [1] 필터 로드",
        "#---------------------------------------"
    ]
    
    current_dir = Path(__file__).resolve().parent.parent
    file_path = current_dir / 'data.json'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for filter_key in data['filters']:
        print_lines.append(f"✓ {filter_key} 필터 로드 완료 (Cross, X)")

    print_lines.extend([
        "",
        "#---------------------------------------",
        "# [2] 패턴 분석 (라벨 정규화 적용)",
        "#---------------------------------------"
    ])

    total_count = len(data['patterns'])
    failed_cases = []

    for p_key, p_val in data['patterns'].items():
        print_lines.append(f"--- {p_key} ---")

        try:
            n = int(p_key.split("_")[1])
        except (IndexError, ValueError):
            reason = f"키 형식 오류: 크기를 추출할 수 없음 ({p_key})"
            print_lines.append(f"판정: FAIL ({reason})")
            failed_cases.append((p_key, reason))
            continue

        filter_group = data.get('filters', {}).get(f"size_{n}")
        if filter_group is None:
            reason = f"필터 size_{n} 없음"
            print_lines.append(f"판정: FAIL ({reason})")
            failed_cases.append((p_key, reason))
            continue

        cross_filter = filter_group.get('cross')
        x_filter = filter_group.get('x')
        pattern_input = p_val.get('input')

        if cross_filter is None or x_filter is None or pattern_input is None:
            reason = f"스키마 오류: size_{n}의 cross/x 필터 또는 패턴 input 누락"
            print_lines.append(f"판정: FAIL ({reason})")
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
            print_lines.append(f"판정: FAIL ({reason})")
            failed_cases.append((p_key, reason))
            continue

        try:
            cross_score = MacCalculator.calculate_2d(cross_filter, pattern_input)
            x_score = MacCalculator.calculate_2d(x_filter, pattern_input)
        except Exception as exc:
            reason = f"연산 오류: {exc}"
            print_lines.append(f"판정: FAIL ({reason})")
            failed_cases.append((p_key, reason))
            continue

        cross_label = LabelNormalizer.normalize("cross")
        x_label = LabelNormalizer.normalize("x")
        expected_label = LabelNormalizer.normalize(p_val.get('expected'))
        verdict = MacCalculator.judge(cross_score, cross_label, x_score, x_label)

        print_lines.extend([f"Cross 점수: {cross_score}", f"X 점수: {x_score}"])

        if expected_label is None:
            result = "FAIL (expected 라벨 인식 불가)"
            failed_cases.append((p_key, f"expected 라벨 인식 불가: {p_val.get('expected')!r}"))
        elif MacCalculator.is_undecided(verdict):
            result = "FAIL (동점 규칙)"
            failed_cases.append((p_key, "동점(UNDECIDED) 처리 규칙에 따라 FAIL"))
        elif verdict == expected_label:
            result = "PASS"
        else:
            result = "FAIL (판정 불일치)"
            failed_cases.append((p_key, f"판정 불일치: 예상 {expected_label}, 실제 {verdict}"))

        print_lines.append(f"판정: {verdict} | expected: {expected_label if expected_label else '알 수 없음'} | {result}",)
            
    print_lines.extend([
        "",
        "#---------------------------------------",
        "# [3] 성능 분석 (평균/10회)",
        "#---------------------------------------",
        "크기       평균 시간(ms)    연산 횟수",
        "-------------------------------------"
    ])

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

        avg_time_ms = BenchmarkUtils.measure_avg_ms(
            lambda bf=bench_filter, bp=bench_pattern: MacCalculator.calculate_2d(bf, bp),
            number=10
        )
        print_lines.append(f"{n}×{n}        {avg_time_ms:.3f}          {n * n}")

    print_lines.extend([
        "",
        "#---------------------------------------",
        "# [4] 결과 요약",
        "#---------------------------------------",
        f"총 테스트: {total_count}개",
        f"통과: {total_count - len(failed_cases)}개",
        f"실패: {len(failed_cases)}개",
        ""
    ])

    if failed_cases:
        print_lines.append("\n실패 케이스:")
        for key, reason in failed_cases:
            print_lines.append(f"- {key}: {reason}")

    OutputUtils.print_lines(print_lines)