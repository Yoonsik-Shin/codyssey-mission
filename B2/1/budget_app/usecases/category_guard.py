from ..errors import CategoryNotFoundError
from ..models.category import Category
from ..repositories.category import CategoryRepository


def ensure_category_exists(category_repo: CategoryRepository, category: str) -> str:
    """등록된 카테고리인지 확인하고 정규화된 이름을 반환. 없으면 CategoryNotFoundError"""
    cleaned_category = Category.normalize_name(category)
    if category_repo.find_by_id(cleaned_category) is None:
        available = [cat.name for cat in category_repo.find_all()]
        raise CategoryNotFoundError(cleaned_category, available)
    return cleaned_category
