class MacCalculator:
    @staticmethod
    def calculate_2d(filter_matrix, pattern_matrix):
        filter_sum = 0
        for f_row, p_row in zip(filter_matrix, pattern_matrix):
            for f_val, p_val in zip(f_row, p_row):
                filter_sum += f_val * p_val
        return filter_sum

    @staticmethod
    def judge(score_a, label_a, score_b, label_b):
        if MacCalculator._is_same_value(score_a, score_b):
            return "UNDECIDED"
        return label_a if score_a > score_b else label_b

    @staticmethod
    def _is_same_value(v1, v2):
        return abs(v1 - v2) < 1e-9
