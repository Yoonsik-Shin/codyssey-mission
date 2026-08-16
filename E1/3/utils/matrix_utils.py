class MatrixUtils:
    @staticmethod
    def get_cell(matrix, row, col):
            return matrix[row][col]

    @staticmethod
    def set_cell(matrix, row, col, value):
        matrix[row][col] = value

    @staticmethod
    def get_cell_1d(flat, row, col, n):
        return flat[row * n + col]

    @staticmethod
    def set_cell_1d(flat, row, col, value, n):
        flat[row * n + col] = value

    @staticmethod
    def flatten(matrix, n):
        flat = [0.0] * (n * n)
        for row in range(n):
            for col in range(n):
                value = MatrixUtils.get_cell(matrix, row, col)
                MatrixUtils.set_cell_1d(flat, row, col, value, n)
        return flat

    @staticmethod
    def generate_cross_pattern(n):
        matrix = [[0.0] * n for _ in range(n)]
        center = n // 2
        for i in range(n):
            matrix[center][i] = 1.0
            matrix[i][center] = 1.0
        return matrix

    @staticmethod
    def generate_x_pattern(n):
        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            matrix[i][i] = 1.0
            matrix[i][n - 1 - i] = 1.0
        return matrix

    def print_pattern(matrix):
        for row in matrix:
            print(' '.join(str(int(v)) for v in row))