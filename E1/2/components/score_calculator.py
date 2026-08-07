class ScoreCalculator:
    """퀴즈 게임의 점수 계산, 백분율 환산 및 최고 기록 판정을 전담하는 클래스"""

    @staticmethod
    def calculate_score(correct_count: int, total_count: int) -> int:
        """맞힌 문제 수와 전체 문제 수를 기반으로 백분율 점수(0~100)를 계산합니다."""
        if total_count <= 0:
            return 0
        return int((correct_count / total_count) * 100)

    @staticmethod
    def is_new_record(current_score: int, best_score: int) -> bool:
        """현재 획득 점수가 이전 최고 점수를 초과했는지 여부를 판단합니다."""
        return current_score > best_score

    @staticmethod
    def create_best_state(score: int, correct: int, total: int) -> dict:
        """최고 점수 상태 객체를 생성합니다."""
        return {
            "score": score,
            "correct": correct,
            "total": total
        }
