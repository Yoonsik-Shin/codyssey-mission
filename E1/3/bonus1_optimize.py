import sys
import timeit
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from main import Utils
from bonus2_generator import generate_cross_pattern


def set_cell_1d(flat, row, col, value, n):
    flat[row * n + col] = value


def get_cell_1d(flat, row, col, n):
    return flat[row * n + col]


def flatten(matrix, n):
    flat = [0.0] * (n * n)
    for row in range(n):
        for col in range(n):
            value = Utils.get_cell(matrix, row, col)
            set_cell_1d(flat, row, col, value, n)
    return flat


def calculate_mac_1d(filter_flat, pattern_flat):
    total = 0
    for f_val, p_val in zip(filter_flat, pattern_flat):
        total += f_val * p_val
    return total


def benchmark_compare(sizes=(3, 5, 13, 25, 50, 100, 200, 400, 800), repeat=10):
    print("\n#---------------------------------------")
    print(f"# 최적화 전(2D) vs 후(1D) 성능 비교 (평균/{repeat}회)")
    print("#---------------------------------------")
    print(f"{'크기':<10}{'2D(ms)':<12}{'1D(ms)':<12}{'개선율':<10}")
    print("-" * 44)

    for n in sizes:
        cross = generate_cross_pattern(n)
        pattern = generate_cross_pattern(n)
        cross_flat = flatten(cross, n)
        pattern_flat = flatten(pattern, n)

        time_2d_sec = min(timeit.repeat(lambda: Utils.calculate_mac(cross, pattern), number=repeat, repeat=5))
        time_1d_sec = min(timeit.repeat(lambda: calculate_mac_1d(cross_flat, pattern_flat), number=repeat, repeat=5))

        avg_2d_ms = time_2d_sec / repeat * 1000
        avg_1d_ms = time_1d_sec / repeat * 1000
        improvement = (avg_2d_ms - avg_1d_ms) / avg_2d_ms * 100 if avg_2d_ms else 0.0

        print(f"{n}x{n:<7}{avg_2d_ms:<12.4f}{avg_1d_ms:<12.4f}{improvement:>6.1f}%")


if __name__ == "__main__":
    print("=== 보너스1: 1차원 배열 메모리 접근 최적화 ===")
    benchmark_compare()
