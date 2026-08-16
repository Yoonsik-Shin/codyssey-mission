class MatrixUtils:
    @staticmethod
    def get_cell(matrix, row, col):
            return matrix[row][col]

    @staticmethod
    def set_cell(matrix, row, col, value):
        matrix[row][col] = value
