class BudgetAppError(Exception):
    """
    애플리케이션 예외의 기본 클래스.
    '무엇이 잘못됐는지'만 담고, '어떻게 고치는지'(CLI 명령 안내)는 CLI 계층이 붙입니다.
    """


class NotFoundError(BudgetAppError):
    """요청한 데이터가 존재하지 않음"""


class TransactionNotFoundError(NotFoundError):
    def __init__(self, tx_id: str):
        super().__init__(f"존재하지 않는 거래 id입니다: '{tx_id}'")
        self.tx_id = tx_id


class CategoryNotFoundError(NotFoundError):
    def __init__(self, name: str, available: list[str]):
        super().__init__(f"등록되지 않은 카테고리입니다: '{name}' (등록된 카테고리: [{', '.join(available)}])")
        self.name = name
        self.available = available


class RecurringRuleNotFoundError(NotFoundError):
    def __init__(self, rule_id: str):
        super().__init__(f"존재하지 않는 반복 내역 id입니다: '{rule_id}'")
        self.rule_id = rule_id


class SourceFileNotFoundError(NotFoundError):
    def __init__(self, path: str):
        super().__init__(f"가져올 파일이 없습니다: {path}")
        self.path = path


class DuplicateCategoryError(BudgetAppError):
    def __init__(self, name: str):
        super().__init__(f"이미 존재하는 카테고리입니다: '{name}'")
        self.name = name


class CategoryInUseError(BudgetAppError):
    def __init__(self, name: str, count: int, rule_count: int = 0):
        usage = f"거래가 {count}건" + (f", 반복 내역이 {rule_count}건" if rule_count else "")
        super().__init__(f"'{name}' 카테고리를 사용하는 {usage} 있어 삭제할 수 없습니다.")
        self.name = name
        self.count = count
        self.rule_count = rule_count


class SameReplacementCategoryError(BudgetAppError):
    def __init__(self, name: str):
        super().__init__(f"대체 카테고리가 삭제할 카테고리와 같습니다: '{name}'")
        self.name = name


class NothingToUpdateError(BudgetAppError):
    def __init__(self):
        super().__init__("수정할 항목이 없습니다.")


class InvalidCsvHeaderError(BudgetAppError):
    def __init__(self, missing: list[str], required: list[str]):
        super().__init__(f"CSV 필수 컬럼이 없습니다: {', '.join(missing)}")
        self.missing = missing
        self.required = required
