class MacCalculator:
    @staticmethod
    def calculate_2d(filter_matrix, pattern_matrix):
        filter_sum = 0
        for f_row, p_row in zip(filter_matrix, pattern_matrix):
            for f_val, p_val in zip(f_row, p_row):
                filter_sum += f_val * p_val
        return filter_sum

    @staticmethod
    def calculate_1d(filter_flat, pattern_flat):
        total = 0
        for f_val, p_val in zip(filter_flat, pattern_flat):
            total += f_val * p_val
        return total

    @staticmethod
    def calculate_cross_sparse(filter_matrix, pattern_matrix, n):
        # 십자가 필터는 중심 행/열 외 전부 0이므로 그 2n-1칸만 곱해서 더하면 됨(중심 칸은 행/열 순회에서 한 번만 더함).
        center = n // 2
        total = 0
        for col in range(n):
            total += filter_matrix[center][col] * pattern_matrix[center][col]
        for row in range(n):
            if row != center:
                total += filter_matrix[row][center] * pattern_matrix[row][center]
        return total

    @staticmethod
    def calculate_x_sparse(filter_matrix, pattern_matrix, n):
        # X 필터는 두 대각선(주대각선/부대각선) 외 전부 0이므로 그 칸만 곱해서 더하면 됨.
        # 홀수 n이면 두 대각선이 중앙에서 겹쳐 2n-1칸, 짝수 n이면 안 겹쳐 2n칸.
        total = 0
        for i in range(n):
            total += filter_matrix[i][i] * pattern_matrix[i][i]
        for i in range(n):
            j = n - 1 - i
            if j != i:
                total += filter_matrix[i][j] * pattern_matrix[i][j]
        return total

    @staticmethod
    def judge(score_a, label_a, score_b, label_b):
        if MacCalculator._is_same_value(score_a, score_b):
            return "UNDECIDED"
        return label_a if score_a > score_b else label_b

    @staticmethod
    def _is_same_value(v1, v2):
        return abs(v1 - v2) < 1e-9
