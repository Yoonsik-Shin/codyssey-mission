import os
from . import commands, repositories, stores, usecases

DEFAULT_DATA_DIR = "./data"


def build_commands(data_dir: str = DEFAULT_DATA_DIR) -> list[commands.BaseCommand]:
    """
    의존성 조립(Composition Root) — 구체 클래스를 아는 유일한 곳.
    Store → Repository → UseCase → Command를 data_dir 기준으로 연결합니다.
    Store는 처음 읽고 쓸 때 파일을 만들므로, 여기서 전부 생성해도 --help는 파일을 건드리지 않습니다.
    """

    def path(filename: str) -> str:
        return os.path.join(data_dir, filename)

    # Repositories — 같은 인스턴스를 여러 UseCase가 공유
    tx_repo = repositories.StoreTransactionRepository(
        stores.CsvStore(path("transactions.csv"), repositories.TRANSACTION_FIELDS),
        stores.SequenceFile(path("transactions.seq")),
    )
    category_repo = repositories.StoreCategoryRepository(
        stores.CsvStore(path("categories.csv"), repositories.CATEGORY_FIELDS),
        defaults=repositories.DEFAULT_CATEGORIES,
    )
    budget_repo = repositories.StoreBudgetRepository(
        stores.CsvStore(path("budgets.csv"), repositories.BUDGET_FIELDS),
    )
    rule_repo = repositories.StoreRecurringRuleRepository(
        stores.CsvStore(path("recurring.csv"), repositories.RECURRING_FIELDS),
        stores.CsvStore(path("recurring_log.csv"), repositories.RECURRING_LOG_FIELDS),
        stores.SequenceFile(path("recurring.seq")),
    )
    csv_file = repositories.TransactionCsvFile()

    # 여러 Command가 함께 쓰는 UseCase
    list_categories = usecases.ListCategoriesUseCase(category_repo)
    monthly_summary = usecases.GetMonthlySummaryUseCase(tx_repo, budget_repo)

    return [
        commands.AddCommand(usecases.AddTransactionUseCase(tx_repo, category_repo), list_categories),
        commands.ListCommand(usecases.ListTransactionsUseCase(tx_repo)),
        commands.SearchCommand(usecases.SearchTransactionsUseCase(tx_repo)),
        commands.SummaryCommand(monthly_summary),
        commands.BudgetCommand(usecases.SetBudgetUseCase(budget_repo), monthly_summary),
        commands.CategoryCommand(
            usecases.AddCategoryUseCase(category_repo),
            list_categories,
            usecases.RemoveCategoryUseCase(category_repo, tx_repo, rule_repo),
        ),
        commands.UpdateCommand(usecases.UpdateTransactionUseCase(tx_repo, category_repo)),
        commands.DeleteCommand(usecases.DeleteTransactionUseCase(tx_repo)),
        commands.ImportCommand(usecases.ImportTransactionsUseCase(tx_repo, category_repo, csv_file)),
        commands.ExportCommand(usecases.ExportTransactionsUseCase(tx_repo, csv_file)),
        commands.RecurringCommand(
            usecases.AddRecurringRuleUseCase(rule_repo, category_repo),
            usecases.ListRecurringRulesUseCase(rule_repo),
            usecases.RemoveRecurringRuleUseCase(rule_repo),
            usecases.ApplyRecurringRulesUseCase(rule_repo, tx_repo, category_repo),
            list_categories,
        ),
    ]
