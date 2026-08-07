import logging
from pathlib import Path

class GameLogger:
    """게임 로그 기록 및 예외 트레이스 관리를 위한 모듈"""
    
    _logger = None

    @classmethod
    def get_logger(cls):
        if cls._logger is None:
            log_dir = Path(__file__).resolve().parent.parent / "logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / "game_error.log"

            cls._logger = logging.getLogger("QuizGame")
            cls._logger.setLevel(logging.ERROR)

            # 파일 핸들러 설정
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)

            cls._logger.addHandler(file_handler)

        return cls._logger

    @classmethod
    def log_error(cls, message: str, exc: Exception = None):
        """예외 발생 시 로그 파일에 기록하고 콘솔용 안내 메시지 반환"""
        logger = cls.get_logger()
        if exc:
            logger.error(f"{message} | Detail: {exc}", exc_info=True)
        else:
            logger.error(message)
