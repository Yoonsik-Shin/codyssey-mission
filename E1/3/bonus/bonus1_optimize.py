import sys
import timeit
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mac_calculator import MacCalculator
from utils.matrix_utils import MatrixUtils
from bonus2_generator import generate_cross_pattern, generate_x_pattern


def verify_sparse_correctness(sizes=(3, 5, 13, 25)):
    print("\n#---------------------------------------")
    print("# O(2N-1) 희소 연산 정확성 검증 (dense 결과와 비교)")
    print("#---------------------------------------")
    for n in sizes:
        cross = generate_cross_pattern(n)
        x = generate_x_pattern(n)

        cross_dense = MacCalculator.calculate_2d(cross, cross)
        cross_sparse = MacCalculator.calculate_cross_sparse(cross, cross, n)
        cross_match = "OK" if abs(cross_dense - cross_sparse) < 1e-9 else "MISMATCH"
        print(f"N={n} Cross: dense={cross_dense}, sparse={cross_sparse} → {cross_match}")

        x_dense = MacCalculator.calculate_2d(x, x)
        x_sparse = MacCalculator.calculate_x_sparse(x, x, n)
        x_match = "OK" if abs(x_dense - x_sparse) < 1e-9 else "MISMATCH"
        print(f"N={n} X:     dense={x_dense}, sparse={x_sparse} → {x_match}")


def benchmark_compare_sparse(sizes=(3, 5, 13, 25, 50, 100, 200, 400, 800), repeat=10):
    print("\n#---------------------------------------")
    print(f"# O(N²) vs O(2N-1) 희소 연산 성능 비교 (Cross/X 필터, 평균/{repeat}회)")
    print("#---------------------------------------")
    print(f"{'크기':<10}{'패턴':<8}{'O(N²)(ms)':<14}{'O(2N-1)(ms)':<14}{'개선율':<10}")
    print("-" * 56)

    for n in sizes:
        cross = generate_cross_pattern(n)
        x = generate_x_pattern(n)

        for label, matrix, sparse_fn in (
            ("Cross", cross, MacCalculator.calculate_cross_sparse),
            ("X", x, MacCalculator.calculate_x_sparse),
        ):
            time_dense_sec = min(timeit.repeat(lambda m=matrix: MacCalculator.calculate_2d(m, m), number=repeat, repeat=5))
            time_sparse_sec = min(timeit.repeat(lambda m=matrix, f=sparse_fn: f(m, m, n), number=repeat, repeat=5))

            avg_dense_ms = time_dense_sec / repeat * 1000
            avg_sparse_ms = time_sparse_sec / repeat * 1000
            improvement = (avg_dense_ms - avg_sparse_ms) / avg_dense_ms * 100 if avg_dense_ms else 0.0

            print(f"{n}x{n:<7}{label:<8}{avg_dense_ms:<14.4f}{avg_sparse_ms:<14.4f}{improvement:>6.1f}%")


def benchmark_compare(sizes=(3, 5, 13, 25, 50, 100, 200, 400, 800), repeat=10):
    print("\n#---------------------------------------")
    print(f"# 최적화 전(2D) vs 후(1D) 성능 비교 (평균/{repeat}회)")
    print("#---------------------------------------")
    print(f"{'크기':<10}{'2D(ms)':<12}{'1D(ms)':<12}{'개선율':<10}")
    print("-" * 44)

    for n in sizes:
        cross = generate_cross_pattern(n)
        pattern = generate_cross_pattern(n)
        cross_flat = MatrixUtils.flatten(cross, n)
        pattern_flat = MatrixUtils.flatten(pattern, n)

        time_2d_sec = min(timeit.repeat(lambda: MacCalculator.calculate_2d(cross, pattern), number=repeat, repeat=5))
        time_1d_sec = min(timeit.repeat(lambda: MacCalculator.calculate_1d(cross_flat, pattern_flat), number=repeat, repeat=5))

        avg_2d_ms = time_2d_sec / repeat * 1000
        avg_1d_ms = time_1d_sec / repeat * 1000
        improvement = (avg_2d_ms - avg_1d_ms) / avg_2d_ms * 100 if avg_2d_ms else 0.0

        print(f"{n}x{n:<7}{avg_2d_ms:<12.4f}{avg_1d_ms:<12.4f}{improvement:>6.1f}%")


if __name__ == "__main__":
    print("=== 보너스1: 1차원 배열 메모리 접근 최적화 ===")
    benchmark_compare()

    print("\n=== 보너스1 추가: Cross/X 패턴 희소성 활용 O(2N-1) 최적화 ===")
    verify_sparse_correctness()
    benchmark_compare_sparse()
