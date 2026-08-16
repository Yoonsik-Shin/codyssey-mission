from utils.matrix_utils import MatrixUtils

class InputUtils:
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
                MatrixUtils.set_cell(matrix, row_idx, col_idx, value)
        return matrix