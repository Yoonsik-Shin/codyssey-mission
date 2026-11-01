from dataclasses import dataclass


@dataclass
class Category:
    name: str

    def __post_init__(self):
        self.name = self.normalize_name(self.name)
        if not self.name:
            raise ValueError("카테고리 이름은 비어있을 수 없습니다.")

    @staticmethod
    def normalize_name(name: str) -> str:
        """카테고리 이름 비교/저장 기준 (앞뒤 공백 제거 + 소문자). 다른 계층도 이 규칙을 재사용합니다."""
        return name.strip().lower()
