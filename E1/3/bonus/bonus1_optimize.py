import sys
import timeit
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mac_calculator import MacCalculator
from utils.matrix_utils import MatrixUtils
from bonus2_generator import generate_cross_pattern


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
