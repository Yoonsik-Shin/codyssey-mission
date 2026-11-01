"""
통합 테스트 — 실제 프로세스로 `python -m budget_app`을 실행하고, 임시 --data-dir의 파일 결과까지 검증합니다.

실행 (B2/1 폴더에서):
    python -m unittest discover -s tests -v
"""
import csv
import os
import subprocess
import sys
import tempfile
import tracemalloc
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class CliTestCase(unittest.TestCase):
    """테스트마다 빈 데이터 폴더를 만들고, CLI를 서브프로세스로 실행하는 헬퍼 제공"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.data_dir = self.tmp / "data"

    def tearDown(self):
        self._tmp.cleanup()

    def run_cli(self, *args: str, stdin: str = "", data_dir: Path | None = None) -> subprocess.CompletedProcess:
        result = subprocess.run(
            [sys.executable, "-m", "budget_app", "--data-dir", str(data_dir or self.data_dir), *args],
            cwd=PROJECT_ROOT,
            input=stdin,
            capture_output=True,
            text=True,
            timeout=30,
        )
        # 어떤 경우에도 스택트레이스가 사용자에게 노출되면 안 됨
        self.assertNotIn("Traceback", result.stdout + result.stderr, msg=result.stderr)
        return result

    def assert_ok(self, result: subprocess.CompletedProcess) -> str:
        self.assertEqual(result.returncode, 0, msg=f"stdout={result.stdout}\nstderr={result.stderr}")
        return result.stdout

    def assert_error(self, result: subprocess.CompletedProcess, code: int = 1) -> str:
        self.assertEqual(result.returncode, code, msg=f"stdout={result.stdout}\nstderr={result.stderr}")
        if code == 1:
            self.assertIn("[오류]", result.stderr)
            self.assertIn("[힌트]", result.stderr)
        return result.stderr

    def add(self, date: str, type_: str, category: str, amount: int, memo: str = "", tags: str = "") -> str:
        out = self.assert_ok(self.run_cli(
            "add", "--date", date, "--type", type_, "--category", category,
            "--amount", str(amount), "--memo", memo, "--tags", tags,
        ))
        self.assertIn("[저장 완료] id=", out)
        return out.strip().split("id=")[-1]

    def read_rows(self, filename: str) -> list[dict]:
        with open(self.data_dir / filename, encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f))

    def seed_sample(self) -> None:
        """2024-01: 수입 3,000,000 / 지출 food 15,000+30,000, transport 20,000, housing 150,000"""
        self.add("2024-01-15", "expense", "food", 15000, "점심", "meal")
        self.add("2024-01-14", "income", "salary", 3000000, "월급")
        self.add("2024-01-12", "expense", "transport", 20000, "", "commute")
        self.add("2024-01-20", "expense", "housing", 150000, "월세", "rent,fixed")
        self.add("2024-01-25", "expense", "food", 30000, "저녁 회식", "meal,team")
        self.add("2024-02-01", "expense", "food", 9000, "점심")


class HelpAndInitTest(CliTestCase):
    def test_all_commands_have_help_and_do_not_touch_files(self):
        self.assertIn("가계부 앱", self.assert_ok(self.run_cli("--help")))
        for command in ["add", "list", "search", "summary", "budget", "category",
                        "update", "delete", "import", "export", "recurring"]:
            with self.subTest(command=command):
                self.assertIn("usage:", self.assert_ok(self.run_cli(command, "--help")))
        for sub in [("budget", "set"), ("budget", "show"), ("category", "add"), ("category", "remove"),
                    ("recurring", "add"), ("recurring", "apply")]:
            self.assert_ok(self.run_cli(*sub, "--help"))
        self.assertFalse(self.data_dir.exists(), "--help만으로 데이터 파일이 생기면 안 됨")

    def test_no_command_prints_help(self):
        self.assertIn("usage:", self.assert_ok(self.run_cli()))
        self.assertIn("usage:", self.assert_ok(self.run_cli("budget")))
        self.assertIn("usage:", self.assert_ok(self.run_cli("category")))

    def test_first_run_creates_files_and_default_categories(self):
        out = self.assert_ok(self.run_cli("category", "list"))
        self.assertIn("[안내] 기본 카테고리를 등록했습니다", out)
        self.assertIn("- food", out)
        self.assertTrue((self.data_dir / "categories.csv").exists())

        out = self.assert_ok(self.run_cli("list"))
        self.assertIn("[안내] 저장 파일이 생성되었습니다", out)
        self.assertIn("등록된 거래가 없습니다", out)

        self.assert_ok(self.run_cli("budget", "set", "--month", "2024-01", "--amount", "1000"))
        for name in ["transactions.csv", "categories.csv", "budgets.csv"]:
            self.assertTrue((self.data_dir / name).exists(), name)

    def test_custom_data_dir(self):
        other = self.tmp / "other"
        self.assert_ok(self.run_cli("category", "list", data_dir=other))
        self.assertTrue((other / "categories.csv").exists())
        self.assertFalse(self.data_dir.exists())

    def test_verbose_logs_execution_time(self):
        result = self.run_cli("--verbose", "category", "list")
        self.assert_ok(result)
        self.assertIn("[로그] CategoryCommand.execute 시작", result.stderr)
        self.assertRegex(result.stderr, r"CategoryCommand\.execute 종료 \(\d+\.\d{3}s\)")


class AddTest(CliTestCase):
    def test_interactive_add_reprompts_invalid_input(self):
        stdin = "\n".join([
            "2024-13-40", "20240115", "2024-01-15",   # 날짜: 잘못된 형식 2번 후 정상
            "expens", "EXPENSE",                       # 타입
            "game", " Food ",                          # 카테고리: 미등록 후 정상(정규화)
            "-5", "abc", "15000",                      # 금액
            "점심", "meal, lunch",                     # 메모, 태그
        ]) + "\n"
        out = self.assert_ok(self.run_cli("add", stdin=stdin))

        self.assertIn("날짜 형식이 올바르지 않습니다: '2024-13-40'", out)
        self.assertIn("날짜 형식이 올바르지 않습니다: '20240115'", out)
        self.assertIn("타입은 income, expense 중 하나여야 합니다", out)
        self.assertIn("등록되지 않은 카테고리입니다: 'game'", out)
        self.assertIn("사용 가능한 카테고리:", out)
        self.assertIn("0보다 큰 양수여야 합니다: -5", out)
        self.assertIn("숫자만 입력 가능합니다: 'abc'", out)
        self.assertIn("[저장 완료] id=TX-000001", out)

        [row] = self.read_rows("transactions.csv")
        self.assertEqual(row, {
            "id": "TX-000001", "type": "expense", "category": "food", "amount": "15000",
            "date": "2024-01-15", "memo": "점심", "tags": "meal,lunch",
        })

    def test_option_add_skips_prompts(self):
        self.assertEqual(self.add("2024-01-15", "income", "salary", 100), "TX-000001")
        self.assertEqual(self.add("2024-01-16", "expense", "food", 200), "TX-000002")

    def test_invalid_option_category_falls_back_to_prompt(self):
        out = self.assert_ok(self.run_cli(
            "add", "--date", "2024-01-15", "--type", "expense", "--category", "game",
            "--amount", "100", "--memo", "", "--tags", "", stdin="food\n",
        ))
        self.assertIn("등록되지 않은 카테고리입니다: 'game'", out)
        self.assertEqual(self.read_rows("transactions.csv")[0]["category"], "food")

    def test_invalid_options_are_rejected_by_argparse(self):
        for args in (["--amount", "0"], ["--amount", "-1"], ["--type", "car"], ["--date", "2024-02-30"]):
            with self.subTest(args=args):
                result = self.run_cli("add", *args)
                self.assert_error(result, code=2)
                self.assertIn("[오류] argument", result.stderr)
                self.assertIn("[힌트]", result.stderr)

    def test_input_closed_midway_is_error_not_traceback(self):
        err = self.assert_error(self.run_cli("add", stdin="2024-01-15\n"))
        self.assertIn("입력이 중간에 종료되었습니다", err)
        self.assertFalse((self.data_dir / "transactions.csv").exists()
                         and self.read_rows("transactions.csv"))


class ListAndSearchTest(CliTestCase):
    def setUp(self):
        super().setUp()
        self.seed_sample()

    def ids(self, out: str) -> list[str]:
        return [line.split(" | ")[0] for line in out.splitlines() if line.startswith("TX-")]

    def test_list_newest_first_with_limit(self):
        out = self.assert_ok(self.run_cli("list", "--limit", "3"))
        self.assertEqual(self.ids(out), ["TX-000006", "TX-000005", "TX-000004"])
        self.assertEqual(len(self.ids(self.assert_ok(self.run_cli("list")))), 6)

    def test_list_same_date_orders_by_id(self):
        self.add("2024-02-01", "expense", "etc", 1)
        self.assertEqual(self.ids(self.assert_ok(self.run_cli("list", "--limit", "2"))),
                         ["TX-000007", "TX-000006"])

    def test_list_columns_are_aligned(self):
        lines = [l for l in self.assert_ok(self.run_cli("list")).splitlines() if l.startswith("TX-")]
        # 금액 컬럼 끝 위치가 모두 같아야 함 (오른쪽 정렬)
        positions = {line.split(" | ")[4] for line in lines}
        self.assertEqual(len({len(p) for p in positions}), 1)

    def test_search_filters(self):
        cases = {
            ("--from", "2024-01-14", "--to", "2024-01-20"): ["TX-000004", "TX-000001", "TX-000002"],
            ("--category", "FOOD"): ["TX-000006", "TX-000005", "TX-000001"],
            ("--type", "income"): ["TX-000002"],
            ("--q", "점심"): ["TX-000006", "TX-000001"],
            ("--tag", "MEAL"): ["TX-000005", "TX-000001"],
            ("--tag", "team", "--category", "food", "--type", "expense"): ["TX-000005"],
            ("--category", "food", "--limit", "1"): ["TX-000006"],
        }
        for args, expected in cases.items():
            with self.subTest(args=args):
                self.assertEqual(self.ids(self.assert_ok(self.run_cli("search", *args))), expected)

    def test_search_no_result_and_invalid_range(self):
        self.assertIn("조건에 맞는 거래가 없습니다", self.assert_ok(self.run_cli("search", "--q", "없는메모")))
        err = self.assert_error(self.run_cli("search", "--from", "2024-02-01", "--to", "2024-01-01"))
        self.assertIn("시작일이 종료일보다 늦습니다", err)


class SummaryAndBudgetTest(CliTestCase):
    def setUp(self):
        super().setUp()
        self.seed_sample()

    def test_summary_totals_and_top_n(self):
        out = self.assert_ok(self.run_cli("summary", "--month", "2024-01", "--top", "2"))
        self.assertIn("총 수입: 3,000,000원", out)
        self.assertIn("총 지출: 215,000원", out)
        self.assertIn("잔액: 2,785,000원", out)
        self.assertIn("예산: 미설정", out)
        self.assertIn("1) housing 150,000원", out)
        self.assertIn("2) food 45,000원", out)
        self.assertNotIn("3)", out)

    def test_summary_month_without_data(self):
        self.assertIn("데이터 없음", self.assert_ok(self.run_cli("summary", "--month", "2023-12")))

    def test_summary_requires_valid_month(self):
        self.assert_error(self.run_cli("summary"), code=2)
        self.assert_error(self.run_cli("summary", "--month", "2024-1"), code=2)
        self.assert_error(self.run_cli("summary", "--month", "2024-13"), code=2)

    def test_budget_usage_and_exceeded_warning(self):
        out = self.assert_ok(self.run_cli("budget", "set", "--month", "2024-01", "--amount", "500000"))
        self.assertIn("[저장 완료] 2024-01 예산 500,000원", out)
        out = self.assert_ok(self.run_cli("summary", "--month", "2024-01"))
        self.assertIn("예산: 500,000원 (사용률 43.0%)", out)
        self.assertIn("남은 예산: 285,000원", out)
        self.assertNotIn("[경고]", out)

        # 같은 월 재설정은 갱신 (행이 늘지 않음)
        self.assert_ok(self.run_cli("budget", "set", "--month", "2024-01", "--amount", "200000"))
        self.assertEqual(len(self.read_rows("budgets.csv")), 1)
        out = self.assert_ok(self.run_cli("budget", "show", "--month", "2024-01"))
        self.assertIn("사용률 107.5%", out)
        self.assertIn("[경고] 예산을 15,000원 초과했습니다", out)

    def test_budget_show_without_budget_and_invalid_amount(self):
        self.assertIn("설정되어 있지 않습니다", self.assert_ok(self.run_cli("budget", "show", "--month", "2024-03")))
        self.assert_error(self.run_cli("budget", "set", "--month", "2024-01", "--amount", "0"), code=2)


class CategoryTest(CliTestCase):
    def test_add_list_and_duplicate(self):
        self.assertIn("[저장 완료] category=cafe", self.assert_ok(self.run_cli("category", "add", "--name", " Cafe ")))
        self.assertIn("[저장 완료] category=book", self.assert_ok(self.run_cli("category", "add", stdin="book\n")))
        self.assertIn("- cafe", self.assert_ok(self.run_cli("category", "list")))
        self.assertIn("이미 존재하는 카테고리", self.assert_error(self.run_cli("category", "add", "--name", "CAFE")))
        self.assertIn("비어있을 수 없습니다", self.assert_error(self.run_cli("category", "add", "--name", "  ")))

    def test_remove_unused_and_nonexistent(self):
        self.assertIn("[삭제 완료] category=shopping",
                      self.assert_ok(self.run_cli("category", "remove", "--name", "Shopping")))
        self.assertNotIn("- shopping", self.assert_ok(self.run_cli("category", "list")))
        self.assertIn("등록되지 않은 카테고리", self.assert_error(self.run_cli("category", "remove", "--name", "nope")))

    def test_remove_in_use_requires_replacement(self):
        self.add("2024-01-01", "expense", "food", 100)
        self.add("2024-01-02", "expense", "food", 200)
        self.add("2024-01-03", "expense", "etc", 300)

        err = self.assert_error(self.run_cli("category", "remove", "--name", "food"))
        self.assertIn("사용하는 거래가 2건", err)
        self.assertIn("--replace-with", err)
        self.assertIn("- food", self.assert_ok(self.run_cli("category", "list")))

        self.assert_error(self.run_cli("category", "remove", "--name", "food", "--replace-with", "nope"))
        self.assert_error(self.run_cli("category", "remove", "--name", "food", "--replace-with", "FOOD"))

        out = self.assert_ok(self.run_cli("category", "remove", "--name", "food", "--replace-with", "ETC"))
        self.assertIn("[이동 완료] 2건의 거래를 'etc'(으)로 옮겼습니다", out)
        self.assertEqual([r["category"] for r in self.read_rows("transactions.csv")], ["etc", "etc", "etc"])
        self.assertNotIn("- food", self.assert_ok(self.run_cli("category", "list")))

    def test_add_transaction_with_new_category(self):
        self.assert_ok(self.run_cli("category", "add", "--name", "cafe"))
        self.add("2024-01-01", "expense", "cafe", 4500)


class UpdateDeleteTest(CliTestCase):
    def setUp(self):
        super().setUp()
        self.add("2024-01-15", "expense", "food", 15000, "점심", "meal")
        self.add("2024-01-16", "income", "salary", 100)

    def test_update_changes_only_given_fields(self):
        out = self.assert_ok(self.run_cli("update", "--id", "TX-000001", "--amount", "18000", "--memo", "점심 (수정)"))
        self.assertIn("[수정 완료] id=TX-000001", out)
        first, second = self.read_rows("transactions.csv")
        self.assertEqual(first, {
            "id": "TX-000001", "type": "expense", "category": "food", "amount": "18000",
            "date": "2024-01-15", "memo": "점심 (수정)", "tags": "meal",
        })
        self.assertEqual(second["amount"], "100")  # 다른 거래는 그대로

        self.assert_ok(self.run_cli("update", "--id", "TX-000001", "--tags", "", "--category", "ETC",
                                    "--date", "2024-01-10", "--type", "income"))
        first = self.read_rows("transactions.csv")[0]
        self.assertEqual((first["tags"], first["category"], first["date"], first["type"]),
                         ("", "etc", "2024-01-10", "income"))

    def test_update_errors(self):
        self.assertIn("존재하지 않는 거래 id", self.assert_error(self.run_cli("update", "--id", "TX-999999", "--amount", "1")))
        self.assertIn("수정할 항목이 없습니다", self.assert_error(self.run_cli("update", "--id", "TX-000001")))
        self.assertIn("등록되지 않은 카테고리", self.assert_error(self.run_cli("update", "--id", "TX-000001", "--category", "nope")))
        self.assert_error(self.run_cli("update", "--amount", "1"), code=2)  # --id 필수
        self.assertEqual(self.read_rows("transactions.csv")[0]["amount"], "15000")

    def test_delete_and_nonexistent(self):
        self.assertIn("[삭제 완료] id=TX-000001", self.assert_ok(self.run_cli("delete", "--id", "TX-000001")))
        self.assertEqual([r["id"] for r in self.read_rows("transactions.csv")], ["TX-000002"])
        self.assertIn("존재하지 않는 거래 id", self.assert_error(self.run_cli("delete", "--id", "TX-000001")))

    def test_deleted_last_id_is_not_reused(self):
        self.assert_ok(self.run_cli("delete", "--id", "TX-000002"))
        self.assertEqual(self.add("2024-01-17", "expense", "etc", 1), "TX-000003")

    def test_no_temp_files_left(self):
        self.assert_ok(self.run_cli("update", "--id", "TX-000001", "--amount", "1"))
        self.assert_ok(self.run_cli("delete", "--id", "TX-000002"))
        self.assertEqual([p.name for p in self.data_dir.iterdir() if p.name.startswith(".tmp-")], [])


class ImportExportTest(CliTestCase):
    def write_csv(self, name: str, text: str) -> Path:
        path = self.tmp / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_import_valid_and_invalid_rows(self):
        path = self.write_csv("in.csv", (
            "date,type,category,amount,memo,tags\n"
            '2024-03-01,expense,ETC,5000,커피,"cafe,morning"\n'
            "2024-03-02,expense,nope,1000,,\n"
            "2024-03-03,income,salary,-1,,\n"
            "20240304,expense,etc,10,,\n"
            "2024-03-05,transfer,etc,10,,\n"
            "2024-03-06,expense,food,abc,,\n"
            "2024-03-07,income,salary,2000000,월급,\n"
        ))
        out = self.assert_ok(self.run_cli("import", "--from", str(path)))
        self.assertIn("[완료] imported=2, skipped=5", out)
        for line_no in (3, 4, 5, 6, 7):
            self.assertIn(f"{line_no}번째 줄", out)

        rows = self.read_rows("transactions.csv")
        self.assertEqual([r["id"] for r in rows], ["TX-000001", "TX-000002"])
        self.assertEqual((rows[0]["category"], rows[0]["tags"]), ("etc", "cafe,morning"))

    def test_import_memo_tags_optional(self):
        path = self.write_csv("min.csv", "date,type,category,amount\n2024-03-01,expense,etc,5000\n")
        self.assertIn("imported=1, skipped=0", self.assert_ok(self.run_cli("import", "--from", str(path))))

    def test_import_file_errors(self):
        self.assertIn("가져올 파일이 없습니다",
                      self.assert_error(self.run_cli("import", "--from", str(self.tmp / "missing.csv"))))
        path = self.write_csv("bad.csv", "date,type,amount\n2024-03-01,expense,100\n")
        self.assertIn("필수 컬럼이 없습니다: category", self.assert_error(self.run_cli("import", "--from", str(path))))

    def test_export_by_month_and_range(self):
        self.add("2024-01-15", "expense", "food", 15000, "점심", "meal,lunch")
        self.add("2024-01-31", "income", "salary", 100)
        self.add("2024-02-01", "expense", "etc", 1)

        out_path = self.tmp / "jan.csv"
        self.assertIn("(2 records)", self.assert_ok(self.run_cli("export", "--out", str(out_path), "--month", "2024-01")))
        with open(out_path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            self.assertEqual(reader.fieldnames, ["date", "type", "category", "amount", "memo", "tags"])
            rows = list(reader)
        self.assertEqual(rows[0], {"date": "2024-01-15", "type": "expense", "category": "food",
                                   "amount": "15000", "memo": "점심", "tags": "meal,lunch"})

        out = self.assert_ok(self.run_cli("export", "--out", str(self.tmp / "r.csv"),
                                          "--from", "2024-01-31", "--to", "2024-02-01"))
        self.assertIn("(2 records)", out)
        self.assertIn("(1 records)", self.assert_ok(self.run_cli("export", "--out", str(self.tmp / "f.csv"),
                                                               "--from", "2024-02-01")))

    def test_export_requires_one_condition(self):
        self.assertIn("기간 조건이 없습니다", self.assert_error(self.run_cli("export", "--out", str(self.tmp / "x.csv"))))
        err = self.assert_error(self.run_cli("export", "--out", str(self.tmp / "x.csv"),
                                             "--month", "2024-01", "--from", "2024-01-01"))
        self.assertIn("함께 쓸 수 없습니다", err)
        self.assertFalse((self.tmp / "x.csv").exists())

    def test_export_refuses_to_overwrite_data_files(self):
        self.add("2024-01-15", "expense", "food", 100)
        tx_file = self.data_dir / "transactions.csv"
        before = tx_file.read_bytes()
        err = self.assert_error(self.run_cli("export", "--out", str(tx_file), "--month", "2024-01"))
        self.assertIn("데이터 폴더 안에는 내보낼 수 없습니다", err)
        self.assertEqual(tx_file.read_bytes(), before)

    def test_export_then_import_roundtrip(self):
        self.seed_sample()
        exported = self.tmp / "all.csv"
        self.assert_ok(self.run_cli("export", "--out", str(exported), "--from", "2000-01-01"))

        other = self.tmp / "other"
        self.assertIn("imported=6, skipped=0", self.assert_ok(self.run_cli("import", "--from", str(exported), data_dir=other)))

        def without_id(path: Path) -> list[dict]:
            with open(path, encoding="utf-8", newline="") as f:
                return [{k: v for k, v in r.items() if k != "id"} for r in csv.DictReader(f)]

        self.assertEqual(without_id(self.data_dir / "transactions.csv"), without_id(other / "transactions.csv"))


class RecurringTest(CliTestCase):
    """보너스: 반복 내역 등록 + 특정 월 자동 생성"""

    def ids(self, out: str) -> list[str]:
        return [line.split(" | ")[0] for line in out.splitlines() if line.startswith("TX-")]

    def add_rule(self, type_: str, category: str, amount: int, day: int, memo: str = "") -> str:
        out = self.assert_ok(self.run_cli("recurring", "add", "--type", type_, "--category", category,
                                          "--amount", str(amount), "--day", str(day), "--memo", memo, "--tags", ""))
        return out.split("id=")[1].split()[0]

    def test_add_list_and_interactive_validation(self):
        self.assertEqual(self.add_rule("income", "salary", 3000000, 25, "월급"), "RC-0001")
        stdin = "\n".join(["expense", "nope", "food", "0", "12000", "32", "15", "구독", "sub"]) + "\n"
        out = self.assert_ok(self.run_cli("recurring", "add", stdin=stdin))
        self.assertIn("등록되지 않은 카테고리입니다: 'nope'", out)
        self.assertIn("0보다 큰 양수여야 합니다: 0", out)
        self.assertIn("일자는 1~31 사이여야 합니다: 32", out)
        self.assertIn("[저장 완료] id=RC-0002", out)

        out = self.assert_ok(self.run_cli("recurring", "list"))
        self.assertIn("RC-0001 | 25일", out)
        self.assertIn("RC-0002 | 15일", out)

    def test_apply_creates_once_and_clamps_to_month_end(self):
        self.add_rule("income", "salary", 3000000, 25, "월급")
        self.add_rule("expense", "housing", 500000, 31, "월세")

        out = self.assert_ok(self.run_cli("recurring", "apply", "--month", "2024-02"))
        self.assertIn("created=2, already=0, skipped=0", out)
        rows = {r["memo"]: r for r in self.read_rows("transactions.csv")}
        self.assertEqual(rows["월세"]["date"], "2024-02-29")      # 31일 → 윤년 2월 말일
        self.assertEqual(rows["월급"]["date"], "2024-02-25")

        out = self.assert_ok(self.run_cli("recurring", "apply", "--month", "2024-02"))
        self.assertIn("created=0, already=2, skipped=0", out)
        self.assertEqual(len(self.read_rows("transactions.csv")), 2)  # 중복 생성 없음

        self.assert_ok(self.run_cli("recurring", "apply", "--month", "2023-04"))
        self.assertIn("2023-04-30", [r["date"] for r in self.read_rows("transactions.csv")])

    def test_apply_skips_rule_with_invalid_category(self):
        self.add_rule("expense", "food", 1000, 1)
        # 파일을 직접 고쳐 카테고리가 사라진 상황을 재현
        rules = self.data_dir / "recurring.csv"
        rules.write_text(rules.read_text(encoding="utf-8").replace(",food,", ",ghost,"), encoding="utf-8")
        out = self.assert_ok(self.run_cli("recurring", "apply", "--month", "2024-01"))
        self.assertIn("RC-0001: 등록되지 않은 카테고리입니다: 'ghost'", out)
        self.assertIn("created=0, already=0, skipped=1", out)

    def test_remove_rule_keeps_created_transactions_and_id_not_reused(self):
        self.add_rule("expense", "food", 1000, 1)
        self.assert_ok(self.run_cli("recurring", "apply", "--month", "2024-01"))
        self.assert_ok(self.run_cli("recurring", "remove", "--id", "RC-0001"))
        self.assertEqual(len(self.read_rows("transactions.csv")), 1)
        self.assertIn("존재하지 않는 반복 내역 id", self.assert_error(self.run_cli("recurring", "remove", "--id", "RC-0001")))
        self.assertEqual(self.add_rule("expense", "food", 1000, 1), "RC-0002")

    def test_category_removal_considers_rules(self):
        self.add_rule("expense", "housing", 500000, 1)
        err = self.assert_error(self.run_cli("category", "remove", "--name", "housing"))
        self.assertIn("반복 내역이 1건", err)
        out = self.assert_ok(self.run_cli("category", "remove", "--name", "housing", "--replace-with", "etc"))
        self.assertIn("1건의 반복 내역을 'etc'(으)로 옮겼습니다", out)
        self.assertIn("| etc", self.assert_ok(self.run_cli("recurring", "list")))


class DataSafetyTest(CliTestCase):
    CORRUPTED_ROW = "TX-000002,expense,food,NOT_A_NUMBER,2024-01-16,,"

    def setUp(self):
        super().setUp()
        self.add("2024-01-15", "expense", "food", 100)
        self.add("2024-01-17", "expense", "food", 300)
        self.tx_file = self.data_dir / "transactions.csv"
        # TX-000002를 손상된 행으로 교체
        lines = self.tx_file.read_text(encoding="utf-8").splitlines()
        lines[2] = self.CORRUPTED_ROW
        self.tx_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_reading_corrupted_row_is_error_and_file_unchanged(self):
        before = self.tx_file.read_bytes()
        for args in (["list"], ["search", "--category", "food"], ["summary", "--month", "2024-01"]):
            with self.subTest(args=args):
                self.assertIn("손상된 거래 데이터", self.assert_error(self.run_cli(*args)))
                self.assertEqual(self.tx_file.read_bytes(), before)

    def test_writing_other_rows_preserves_corrupted_row(self):
        # update/delete는 원시 행을 그대로 넘기며 재작성하므로, 손상된 행도 사라지지 않고 보존돼야 함
        self.assert_ok(self.run_cli("update", "--id", "TX-000001", "--amount", "5"))
        self.assertIn(self.CORRUPTED_ROW, self.tx_file.read_text(encoding="utf-8"))

        self.assert_ok(self.run_cli("delete", "--id", "TX-000001"))
        content = self.tx_file.read_text(encoding="utf-8")
        self.assertIn(self.CORRUPTED_ROW, content)
        self.assertNotIn("TX-000001", content)


class ArchitectureTest(unittest.TestCase):
    """계층 의존 방향과 CLI 지식의 위치를 코드 수준에서 고정"""

    PACKAGE = PROJECT_ROOT / "budget_app"
    # 계층 → import하면 안 되는 계층
    FORBIDDEN = {
        "models": {"repositories", "stores", "usecases", "commands", "container", "cli"},
        "stores": {"models", "repositories", "usecases", "commands", "container", "cli"},
        "repositories": {"usecases", "commands", "container", "cli"},
        "usecases": {"commands", "stores", "container", "cli"},
    }

    def imported_layers(self, path: Path) -> set[str]:
        import ast
        layers = set()
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.level > 0 and node.module:
                layers.add(node.module.split(".")[0])
        return layers

    def test_dependency_direction(self):
        for layer, forbidden in self.FORBIDDEN.items():
            for path in (self.PACKAGE / layer).glob("*.py"):
                with self.subTest(file=f"{layer}/{path.name}"):
                    # 같은 계층 내부 import(from .x)는 module 첫 마디가 같은 계층 파일명이므로 제외 대상 아님
                    violations = self.imported_layers(path) & forbidden
                    self.assertFalse(violations, f"{layer}/{path.name} → {violations}")

    def test_cli_knowledge_stays_in_cli_layer(self):
        for layer in ("models", "repositories", "stores", "usecases"):
            for path in (self.PACKAGE / layer).glob("*.py"):
                with self.subTest(file=f"{layer}/{path.name}"):
                    source = path.read_text(encoding="utf-8")
                    self.assertNotIn("python -m budget_app", source)
                    self.assertNotRegex(source, r"['\"]--[a-z]", "CLI 옵션 이름은 commands/에만")


class MonthTest(unittest.TestCase):
    """Month 값 객체 (프로세스 내부 실행)"""

    def test_parse_of_and_range(self):
        sys.path.insert(0, str(PROJECT_ROOT))
        from datetime import date
        from budget_app.models.period import Month

        feb = Month.parse(" 2024-02 ")
        self.assertEqual(str(feb), "2024-02")
        self.assertEqual((feb.first_day, feb.last_day), (date(2024, 2, 1), date(2024, 2, 29)))  # 윤년
        self.assertEqual(Month.parse("2023-02").last_day, date(2023, 2, 28))
        self.assertEqual(Month.of(date(2024, 2, 15)), feb)
        self.assertLess(Month.parse("2023-12"), feb)
        for bad in ("2024-1", "2024-13", "2024-00", "202401", "abcd-ef"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                Month.parse(bad)


class StreamingTest(unittest.TestCase):
    """list가 파일 전체를 메모리에 올리지 않는지 tracemalloc으로 확인 (프로세스 내부 실행)"""

    def test_list_memory_does_not_grow_with_file_size(self):
        sys.path.insert(0, str(PROJECT_ROOT))
        from budget_app.repositories.transaction import TRANSACTION_FIELDS, StoreTransactionRepository
        from budget_app.stores.csv_file import write_csv_rows
        from budget_app.stores.csv_store import CsvStore
        from budget_app.stores.sequence_file import SequenceFile
        from budget_app.usecases.list_transactions import ListTransactionsUseCase

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "transactions.csv")
            count = 50_000
            write_csv_rows(path, TRANSACTION_FIELDS, (
                {"id": f"TX-{i:06d}", "type": "expense", "category": "food", "amount": i,
                 "date": f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}", "memo": "메모" * 5, "tags": "a,b"}
                for i in range(1, count + 1)
            ))
            repo = StoreTransactionRepository(CsvStore(path, TRANSACTION_FIELDS), SequenceFile(os.path.join(tmp, "s")))

            tracemalloc.start()
            latest = ListTransactionsUseCase(repo).execute(limit=10)
            _, streaming_peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            tracemalloc.start()
            everything = repo.find_all()
            _, full_load_peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

        self.assertEqual(len(latest), 10)
        self.assertEqual(len(everything), count)
        self.assertTrue(all(tx.date.isoformat() == "2024-12-28" for tx in latest[:1]))
        # 스트리밍은 전체 로드 대비 훨씬 적은 메모리를 써야 함
        self.assertLess(streaming_peak * 10, full_load_peak,
                        msg=f"streaming={streaming_peak:,}B full={full_load_peak:,}B")


if __name__ == "__main__":
    unittest.main()
