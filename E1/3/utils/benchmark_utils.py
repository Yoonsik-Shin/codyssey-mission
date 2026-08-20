import timeit

class BenchmarkUtils:
    @staticmethod
    def measure_avg_ms(fn, number=10):
        total_time_sec = timeit.timeit(fn, number=number)
        return (total_time_sec / number) * 1000
