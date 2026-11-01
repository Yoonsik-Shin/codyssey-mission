from ..errors import DuplicateCategoryError
from ..models.category import Category
from ..repositories.category import CategoryRepository


class AddCategoryUseCase:
    """
    카테고리 추가 유스케이스.
    중복 여부 검증 후 새 Category를 저장합니다.
    """

    def __init__(self, category_repo: CategoryRepository):
        self._category_repo = category_repo

    def execute(self, name: str) -> Category:
        category = Category(name=name)

        if self._category_repo.find_by_id(category.name) is not None:
            raise DuplicateCategoryError(category.name)

        return self._category_repo.save(category)
