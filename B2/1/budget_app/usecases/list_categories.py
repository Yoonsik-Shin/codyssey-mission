from ..repositories.category import CategoryRepository


class ListCategoriesUseCase:
    """
    카테고리 목록 조회 유스케이스.
    등록된 모든 카테고리 이름을 반환합니다.
    """

    def __init__(self, category_repo: CategoryRepository):
        self._category_repo = category_repo

    def execute(self) -> list[str]:
        return [cat.name for cat in self._category_repo.find_all()]
