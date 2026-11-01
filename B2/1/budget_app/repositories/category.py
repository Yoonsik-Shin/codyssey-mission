from typing import override
from .base import BaseRepository
from ..stores.base import BaseStore
from ..models.category import Category

# 초기 기본 제공 카테고리 목록
DEFAULT_CATEGORIES = ["food", "transport", "housing", "salary", "shopping", "etc"]
CATEGORY_FIELDS = ["name"]


class CategoryRepository(BaseRepository[Category]):
    """카테고리 영속화 전용 리포지토리 인터페이스"""
    pass


class StoreCategoryRepository(CategoryRepository):
    """BaseStore(CsvStore 등)를 통한 카테고리 CRUD 구현체"""

    def __init__(self, store: BaseStore, defaults: list[str] | None = None):
        self._store = store
        self._defaults = defaults or []

    def _load(self) -> list[dict]:
        """
        초기 실행 정책 (안 A): 카테고리 파일이 없으면 기본 카테고리를 자동 생성한 뒤 읽습니다.
        """
        if self._defaults and not self._store.exists():
            self._store.save({"name": name} for name in self._defaults)
            print(f"[안내] 기본 카테고리를 등록했습니다: {', '.join(self._defaults)}")
        return self._store.load()

    @override
    def save(self, entity: Category) -> Category:
        if self.find_by_id(entity.name) is None:
            self._store.append({"name": entity.name})
        return entity  # 이미 존재하면 그대로 반환

    @override
    def find_all(self) -> list[Category]:
        items = self._load()
        return [Category(name=item["name"]) for item in items if item.get("name")]

    @override
    def find_by_id(self, entity_id: str) -> Category | None:
        """이름으로 카테고리 검색"""
        items = self._load()
        target = Category.normalize_name(entity_id)
        for item in items:
            if item.get("name") == target:
                return Category(name=item["name"])
        return None

    @override
    def delete(self, entity_id: str) -> bool:
        items = self._load()
        target = Category.normalize_name(entity_id)
        new_items = [item for item in items if item.get("name") != target]
        if len(new_items) != len(items):
            self._store.save(new_items)
            return True
        return False

