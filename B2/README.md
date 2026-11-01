# 가계부 애플리케이션 (Budget App)

파일(CSV) 기반 콘솔 가계부. 표준 라이브러리만 사용합니다.

- [1. 사용 방법](#1-사용-방법) — 실행, 저장 파일, 명령 예시, CSV 스키마, 동작 확인 시나리오
- [2. 아키텍처](#2-아키텍처) — 계층 구조와 책임
- [3. 설계 결정 기록](#3-설계-결정-기록) — 구조가 지금 모양이 되기까지의 질문과 결론
- [4. 핵심 개념 정리](#4-핵심-개념-정리) — 구현에 쓰인 Python 문법/개념
- [5. 과제 목표별 설명](#5-과제-목표별-설명) — 저장/CRUD, 계층 책임, 제너레이터, 데코레이터, 타입 힌트

---

## 1. 사용 방법

### 실행

- **Python 3.12 이상** (`typing.override` 사용)
- `B2/1` 폴더에서 실행합니다.

```bash
cd B2/1
python -m budget_app --help                          # 전체 명령 목록
python -m budget_app <command> --help                # 명령별 사용법
python -m budget_app --data-dir ./mydata list        # 저장 폴더 변경
python -m budget_app --verbose summary --month 2024-01   # 실행 로그 + 소요 시간 출력
```

- 전역 옵션(`--data-dir`, `--verbose`)은 **명령어 앞**에 씁니다.
- 종료 코드: 정상 `0`, 오류 `1`, 인자 오류(argparse) `2`, Ctrl+C `130`
- 통합 테스트 (`B2/1`에서, 임시 폴더를 쓰므로 `./data`는 건드리지 않음):

  ```bash
  python -m unittest discover -s tests -v
  ```

### 저장 파일

| 파일 | 내용 | 컬럼 |
| --- | --- | --- |
| `<data-dir>/transactions.csv` | 거래 내역 | `id,type,category,amount,date,memo,tags` |
| `<data-dir>/categories.csv` | 카테고리 목록 | `name` |
| `<data-dir>/budgets.csv` | 월 예산 | `id,month,category,amount` (`id` = `YYYY-MM:all`) |
| `<data-dir>/transactions.seq` | 마지막으로 발급한 거래 id 순번 | 숫자 1개 |

- 형식: CSV, UTF-8, 헤더 포함. 기본 폴더는 `./data`
- **초기 실행**: 파일이 없으면 처음 읽거나 쓸 때 자동 생성하고 `[안내]` 메시지를 출력합니다. 카테고리 파일이 없으면 기본 카테고리(`food, transport, housing, salary, shopping, etc`)를 자동 등록합니다 (안 A).
- **안전한 저장**: 수정/삭제는 임시 파일에 전체를 쓴 뒤 `os.replace`로 교체(원자적 교체)합니다. 중간에 실패해도 원본이 깨지지 않습니다. 추가는 파일 끝에 한 줄 append 합니다.
- 거래 id(`TX-000001`)는 삭제 후에도 재사용되지 않습니다 (`transactions.seq`).

### 주요 명령 예시

```bash
# 거래 추가 — 기본은 대화형. 옵션으로 넘긴 항목은 묻지 않음
python -m budget_app add
python -m budget_app add --date 2024-01-15 --type expense --category food --amount 15000 --memo 점심 --tags meal

# 목록 (최신순, 기본 20건)
python -m budget_app list --limit 3

# 검색 (모든 조건 AND, 최신순)
python -m budget_app search --from 2024-01-01 --to 2024-01-31 --type expense --category food --q 점심 --tag meal

# 예산 + 월별 요약 (예산 사용률 / 초과 경고)
python -m budget_app budget set --month 2024-01 --amount 500000
python -m budget_app budget show --month 2024-01
python -m budget_app summary --month 2024-01 --top 3

# 카테고리
python -m budget_app category add                                   # 대화형 (카테고리명: )
python -m budget_app category add --name cafe
python -m budget_app category list
python -m budget_app category remove --name cafe                    # 사용 중이면 삭제 거부
python -m budget_app category remove --name cafe --replace-with food # 거래를 food로 옮긴 뒤 삭제

# 수정 — 옵션 방식(안 A)으로 고정. 지정한 필드만 바뀜
python -m budget_app update --id TX-000001 --amount 18000 --memo "점심 (수정)"

# 삭제
python -m budget_app delete --id TX-000001

# 가져오기 / 내보내기
python -m budget_app import --from import.csv
python -m budget_app export --out export.csv --month 2024-01
python -m budget_app export --out export.csv --from 2024-01-01 --to 2024-03-31
```

### import/export CSV 스키마

| column | required | 설명 |
| --- | --- | --- |
| `date` | Y | `YYYY-MM-DD` |
| `type` | Y | `income` / `expense` |
| `category` | Y | 등록된 카테고리 |
| `amount` | Y | 양수 정수 |
| `memo` | N | 문자열 |
| `tags` | N | 쉼표(`,`) 구분 문자열 (CSV에서는 `"a,b"`처럼 따옴표로 감쌈) |

- 공통: UTF-8, 헤더 포함. `id`는 포함하지 않으며 import 시 새로 발급합니다.
- import: 잘못된 행은 줄 번호와 사유를 출력하고 건너뜁니다 (`imported=N, skipped=M`). 통과한 행은 한 번에 원자적으로 저장합니다.
- export: `--month` 또는 `--from/--to` 중 하나는 필수입니다. `--month`와 `--from/--to`는 함께 쓸 수 없습니다.

### 오류 출력

스택트레이스 대신 원인과 해결 힌트를 출력합니다.

```text
$ python -m budget_app delete --id TX-999999
[오류] 존재하지 않는 거래 id입니다: 'TX-999999'
[힌트] 'python -m budget_app list'로 id를 확인하세요.
```

없는 명령이나 잘못된 옵션(argparse 단계 오류)도 같은 형식으로 출력하고 종료 코드 2로 끝납니다.

```text
$ python -m budget_app app
usage: budget_app [-h] [--data-dir DATA_DIR] [--verbose] {add,list,...} ...
[오류] argument command: invalid choice: 'app' (choose from add, list, search, ...)
[힌트] 'python -m budget_app --help'로 사용법을 확인하세요.
```

대화형 입력에서 형식이 틀리면 올바른 값이 들어올 때까지 다시 묻습니다.

```text
날짜(YYYY-MM-DD): 2024-13-40
❌ 날짜 형식이 올바르지 않습니다: '2024-13-40' (YYYY-MM-DD 형식, 예: 2024-01-15)
날짜(YYYY-MM-DD):
```

### 동작 확인 시나리오

직접 실행해 보며 기능을 확인하는 순서입니다. `--data-dir ./try`로 별도 폴더를 쓰므로 실제 `./data`는 건드리지 않습니다. **위에서부터 순서대로** 실행해야 id와 금액이 주석과 일치합니다.

#### 준비

```bash
cd B2/1
alias b='python3 -m budget_app --data-dir ./try'
```

#### ① 도움말 · 초기 실행

```bash
b --help
b add --help
b category --help
ls try                 # 폴더 없음 — --help는 파일을 만들지 않음
b category list        # [안내] 기본 카테고리 등록 + 목록
```

#### ② 거래 추가 — 대화형

```bash
b add
```

일부러 틀린 값을 넣어 보세요. 틀릴 때마다 ❌ 안내 후 다시 묻습니다.

| 질문 | 입력 순서 |
| --- | --- |
| 날짜 | `2024-13-40` → `20240115` → `2024-01-15` |
| 타입 | `expens` → `expense` |
| 카테고리 | `game` (사용 가능 목록 안내) → `food` |
| 금액 | `-5` → `abc` → `15000` |
| 메모 | `점심` |
| 태그 | `meal` |

→ `[저장 완료] id=TX-000001`

#### ③ 거래 추가 — 옵션 방식

```bash
b add --date 2024-01-14 --type income  --category salary    --amount 3000000 --memo 월급       --tags ""
b add --date 2024-01-12 --type expense --category transport --amount 20000   --memo ""         --tags commute
b add --date 2024-01-20 --type expense --category housing   --amount 150000  --memo 월세       --tags rent,fixed
b add --date 2024-01-25 --type expense --category food      --amount 30000   --memo "저녁 회식" --tags meal,team
b add --date 2024-02-01 --type expense --category food      --amount 9000    --memo 점심       --tags ""
```

→ TX-000002 ~ TX-000006

#### ④ 목록 · 검색

```bash
b list                                            # 6건, 최신순, 컬럼 정렬
b list --limit 3                                  # 000006, 000005, 000004
b search --from 2024-01-14 --to 2024-01-20        # 000004, 000001, 000002
b search --category FOOD                          # 대소문자 무시: 000006, 000005, 000001
b search --type income                            # 000002
b search --q 점심                                 # 000006, 000001
b search --tag meal --category food --limit 1     # 000005
b search --q 없는메모                             # 조건에 맞는 거래가 없습니다
b search --from 2024-02-01 --to 2024-01-01        # [오류] 시작일이 종료일보다 늦습니다
```

#### ⑤ 월별 요약 · 예산

```bash
b summary --month 2024-01 --top 3    # 수입 3,000,000 / 지출 215,000 / 잔액 2,785,000 / 예산 미설정
b summary --month 2023-12            # 데이터 없음
b budget set --month 2024-01 --amount 500000
b summary --month 2024-01            # 예산 500,000원 (사용률 43.0%), 남은 예산 285,000원
b budget set --month 2024-01 --amount 200000      # 같은 월 → 갱신
b budget show --month 2024-01        # 사용률 107.5% + ⚠️ 15,000원 초과 경고
cat try/budgets.csv                  # 2024-01 행 1개
```

#### ⑥ 카테고리

```bash
b category add --name Cafe           # category=cafe (소문자 정규화)
b category add                       # 대화형: 카테고리명 입력
b category add --name CAFE           # [오류] 이미 존재
b category remove --name shopping    # 쓰는 거래 없음 → 바로 삭제
b category remove --name food        # [오류] 사용 중 3건 + --replace-with 힌트
b category remove --name food --replace-with etc   # 3건 이동 후 삭제
b category list
b list                               # 이전 food 거래가 etc로 바뀜
```

#### ⑦ 수정 · 삭제

```bash
b update --id TX-000001 --amount 18000 --memo "점심 (수정)"
b list --limit 10                    # TX-000001만 바뀜
b update --id TX-000001              # [오류] 수정할 항목이 없습니다
b update --id TX-999999 --amount 1   # [오류] 존재하지 않는 거래 id
b update --id TX-000001 --category nope   # [오류] 등록되지 않은 카테고리
b delete --id TX-000006
b delete --id TX-000006              # [오류] 존재하지 않는 거래 id
b add --date 2024-02-02 --type expense --category etc --amount 1000 --memo "" --tags ""
                                     # TX-000007 (지운 006을 재사용하지 않음)
```

#### ⑧ 내보내기 · 가져오기

```bash
b export --out jan.csv --month 2024-01
cat jan.csv                          # date,type,category,amount,memo,tags (id 없음)
b export --out range.csv --from 2024-01-20 --to 2024-02-28
b export --out x.csv                 # [오류] 기간 조건이 없습니다
b export --out x.csv --month 2024-01 --from 2024-01-01   # [오류] 함께 쓸 수 없습니다
b export --out try/transactions.csv --month 2024-01      # [오류] 데이터 폴더 안에는 내보낼 수 없습니다

printf 'date,type,category,amount,memo,tags\n2024-03-01,expense,etc,5000,커피,"cafe,morning"\n2024-03-02,expense,nope,1000,,\n2024-03-03,income,salary,-1,,\nbad,expense,etc,10,,\n' > in.csv
b import --from in.csv               # 3줄 건너뜀 사유 출력, imported=1, skipped=3
b import --from missing.csv          # [오류] 가져올 파일이 없습니다
```

#### ⑨ 오류 처리 · 종료 코드

```bash
b app; echo "exit=$?"                           # 없는 명령: [오류]/[힌트], exit=2
b summary --month 2024-1; echo "exit=$?"        # 인자 형식 오류, exit=2
b add --amount 0; echo "exit=$?"                # exit=2
b delete --id TX-999999; echo "exit=$?"         # [오류]/[힌트], exit=1
b list; echo "exit=$?"                          # exit=0
b add                                           # 입력 도중 Ctrl+C
echo "exit=$?"                                  # [취소], exit=130
b --verbose list --limit 2                      # [로그] 실행 시작/종료 (소요 시간)
```

#### ⑩ 자동 테스트 · 정리

```bash
python3 -m unittest discover -s tests -v
rm -rf try jan.csv range.csv in.csv
unalias b
```

---

## 2. 아키텍처

### 계층 구조

```text
__main__.py → cli.main()          @handle_errors: 예외 → [오류] 원인 / [힌트] CLI 사용법 + 종료 코드
                 │
                 ├─ bootstrap.build_commands(data_dir)   의존성 조립 (Composition Root)
                 ▼
[Command]      commands/       입력 형식 검증 + UseCase 호출 + 출력      @log_execution
    │
    ▼
[UseCase]      usecases/       사용자 동작 1개 = 클래스 1개. 흐름 조율
    │    └──>  [Model]  models/  엔티티 · 값 객체 · 도메인 규칙 (Repository를 모름)
    ▼
[Repository]   repositories/   도메인 객체 ↔ dict 변환, ID 채번
    │
    ▼
[Store]        stores/         파일 I/O (스트리밍 읽기, 원자적 쓰기)
    │
    ▼
 ./data/*.csv
```

| 계층 | 하는 일 | 하지 않는 일 |
| --- | --- | --- |
| **Command** | argparse 설정, 형식 검증(날짜/숫자/Enum), 대화형 재입력, 결과 출력 | 비즈니스 판단, 파일 접근 |
| **UseCase** | 데이터를 가져와 → 도메인에 맡기고 → 저장. 저장소에 물어봐야 아는 검증 (카테고리/id 존재) | `input()`/`print()`, 파일 형식 |
| **Model** | 자기 데이터만으로 판단 가능한 규칙과 계산 (금액 양수, 예산 사용률, 월별 집계, 검색 조건) | Repository 호출, I/O |
| **Repository** | 도메인 객체 ↔ 원시 dict 변환, ID 채번, 컬렉션처럼 보이는 인터페이스 | 비즈니스 규칙 |
| **Store** | 실제 파일 읽기/쓰기 (CSV, JSONL) | 도메인 객체를 앎 |

의존 방향은 항상 바깥(Command)에서 안쪽(Model)입니다. 바깥 계층은 안쪽의 도메인 타입(`TransactionType`, `Category.normalize_name` 등)을 써도 되지만, 그 반대는 안 됩니다.

### 디렉토리

```text
budget_app/
├── __main__.py            # python -m budget_app 진입점 (cli.main 호출만)
├── cli.py                 # argparse 구성, --data-dir/--verbose 처리
├── bootstrap.py           # build_commands(): Store → Repository → UseCase → Command 조립
├── decorators.py          # @log_execution (범용 공통 관심사)
├── errors.py              # 애플리케이션 예외 — '무엇이 잘못됐는지'만 (CLI 안내 없음)
├── commands/              # ── CLI 계층 (입력 · 출력 · 사용법 안내는 전부 여기)
│   ├── base.py            # BaseCommand
│   ├── arg_types.py       # 입력: parse_date/parse_month/parse_type/parse_positive_int, ask()
│   ├── formatters.py      # 출력: 콘솔 테이블 정렬(한글 폭 고려), 금액/예산 출력
│   ├── error_handler.py   # @handle_errors, hint_for(예외 → CLI 사용법 안내), UsageError
│   ├── add.py  list.py  search.py  summary.py  budget.py  category.py
│   └── update.py  delete.py  import_csv.py  export_csv.py
├── usecases/
│   ├── add_transaction.py  list_transactions.py  search_transactions.py
│   ├── update_transaction.py  delete_transaction.py  get_monthly_summary.py
│   ├── set_budget.py  add_category.py  list_categories.py  remove_category.py
│   ├── import_transactions.py  export_transactions.py
│   └── category_guard.py  # ensure_category_exists(): 여러 UseCase가 쓰는 존재 검증
├── models/
│   ├── transaction.py     # Transaction, TransactionType, create(), recency_key()
│   ├── category.py        # Category, normalize_name()
│   ├── budget.py          # Budget, evaluate() → BudgetStatus
│   ├── summary.py         # MonthlySummary.from_transactions()
│   ├── transaction_query.py  # TransactionQuery.matches(), for_month()
│   └── period.py          # Month 값 객체(parse/of/first_day/last_day), parse_date — 기간 도메인 규칙
├── repositories/
│   ├── base.py            # BaseRepository[T]
│   ├── transaction.py  category.py  budget.py   # budget: find_by_month() — 저장 키 형식은 여기만 앎
│   └── transaction_csv.py # import/export CSV 어댑터 (UseCase에 주입): 스키마, 헤더 검증, 행 ↔ Transaction
└── stores/                # 도메인 객체를 모름 (dict만)
    ├── base.py            # BaseStore
    ├── csv_store.py  jsonl_store.py
    ├── csv_file.py        # stores 내부 헬퍼: read_csv_rows (제너레이터), write_csv_rows (원자적)
    └── sequence_file.py   # 마지막 발급 id 순번
```

---

## 3. 설계 결정 기록

구현하면서 나온 질문과 결론을 순서대로 정리했습니다. 앞에서 내린 결론이 뒤에서 바뀐 경우가 있으므로, 각 항목의 **최종** 표시가 현재 코드 기준입니다.

### 3.1 `ModuleNotFoundError: No module named 'commands'`

```bash
$ python3 -m budget_app add
  File ".../budget_app/__main__.py", line 1, in <module>
    from commands import COMMAND_LIST
ModuleNotFoundError: No module named 'commands'
```

- `python -m budget_app`은 **실행한 위치(CWD, `B2/1`)**를 `sys.path[0]`에 넣습니다. 그래서 최상위에서 찾을 수 있는 패키지는 `budget_app`뿐이고, `commands`는 그 하위 패키지라 최상위 이름으로는 찾지 못합니다.
- 파일이 같은 폴더에 있어도, 절대 import는 파일 위치가 아니라 **`sys.path`** 기준으로 동작합니다.
- **최종**: 패키지 내부는 상대 import(`from .cli import main`, `from .base import BaseCommand`)를 씁니다.

| 실행 명령어 | `sys.path[0]` | 상대 import |
| --- | --- | --- |
| `python3 -m budget_app add` (권장) | CWD (`B2/1`) | 가능 (`__package__ == 'budget_app'`) |
| `python3 budget_app/__main__.py` | 파일 위치 (`budget_app/`) | 불가 (`attempted relative import with no known parent package`) |

IDE의 `Could not resolve relative import '..'` 경고도 같은 원인입니다. IDE가 `B2/1`을 패키지 루트로 인식하지 못해서 나는 경고이고, `python -m`으로 실행하면 문제없습니다.

### 3.2 `cli.py`와 `__main__.py` 분리

- `__main__.py`: `python -m budget_app`이 실행하는 최소 진입점. `main()` 호출만 합니다.
- `cli.py`: 파서 구성과 실행 흐름을 담은 일반 모듈. 테스트에서 `main(["list"])`처럼 프로세스 없이 호출할 수 있고, 배포 시 `console_scripts = ["budget_app = budget_app.cli:main"]`로 지정할 수 있습니다.
- `cli.py` 하단의 `if __name__ == "__main__": main()`은 **제거**했습니다. 상대 import 때문에 `python cli.py`로는 어차피 실행되지 않는 죽은 코드이고, 진입점은 `__main__.py` 하나면 됩니다.
- 함수 안에서 다른 함수를 호출할 때는 정의 순서가 상관없습니다. `def`는 모듈 로드 시 등록만 하고, 실제 호출 시점에는 모든 함수가 이미 등록돼 있기 때문입니다. 그래서 중요한 `main()`을 위에, `_build_parser()` 같은 헬퍼를 아래에 둡니다. 단, 모듈 최상단에서 즉시 실행하는 코드는 순서가 중요합니다.

### 3.3 Store vs Repository

| 구분 | Repository | Store |
| --- | --- | --- |
| 기원 | DDD (도메인 주도 설계) | 파일/DB I/O |
| 관점 | 도메인 — 메모리 위의 컬렉션처럼 다룸 | 인프라 — 실제 저장 매체 |
| 다루는 단위 | 도메인 객체 (`Transaction`) | 원시 데이터 (`dict`) |
| 대표 메서드 | `save(tx)`, `find_by_id(id)`, `stream()` | `stream()`, `save(rows)`, `append(row)` |

- Store는 "파일을 어떻게 읽고 쓰나"만 알고, Repository는 "거래를 어떻게 저장/조회하나"를 도메인 언어로 제공합니다.
- 덕분에 CSV → JSONL로 바꿀 때 Repository 이하만 바꾸면 되고, UseCase는 그대로입니다 (`CsvStore`와 `JsonlStore` 모두 `BaseStore` 구현).
- `save()`는 저장된 엔티티를 **반환**합니다. 저장 과정에서 채번된 id처럼 저장소가 채운 값을 호출자가 받아야 하기 때문입니다.

### 3.4 저장 포맷: JSON vs JSONL vs CSV

- **JSON**: 파일 전체가 배열 하나(`[...]`). 한 건을 읽든 추가하든 전체를 파싱해야 합니다. 초기에 만든 `json_store.py`는 이 방식이라 JSONL을 처리할 수 없었고, 쓰이지 않아 삭제했습니다.
- **JSONL**: 한 줄에 JSON 객체 하나. 줄 단위 스트리밍과 append에 유리합니다.
- **CSV**: 헤더 + 콤마 구분. 스프레드시트와 호환되고, import/export 스키마와 같은 형식입니다.
- **최종**: 저장 포맷은 **CSV**로 선택했습니다. `JsonlStore`는 대체 구현으로 남겨 두었습니다.

### 3.5 Command와 Service의 역할 → UseCase

처음 질문은 "Command는 args 검증, Service는 비즈니스 로직인가?"였습니다. 웹의 Controller/Service와 같은 구분입니다.

- **Command — 형식(Syntax) 검증**: 숫자인가, `YYYY-MM-DD`인가, `income/expense` 중 하나인가
- **비즈니스 검증**: 금액이 양수인가, 등록된 카테고리인가, 예산을 초과했나

이 구분은 그대로 유지했고, "비즈니스 쪽"이 어디에 사는지는 아래(3.10 ~ 3.12)를 거치며 바뀌었습니다.

### 3.6 `TransactionType`은 Enum으로, Command가 알아도 되나?

- `if t in ("income", "expense")` 같은 하드코딩 대신 `TransactionType` Enum을 **단일 진실 공급원(SSOT)**으로 씁니다. 타입이 추가되면 Enum만 고치면 되고, 도움말·프롬프트·검증 메시지가 자동으로 따라옵니다.
- Command가 도메인 Enum을 아는 것은 **문제없습니다**. 의존 방향이 바깥(CLI) → 안쪽(도메인)이고, CLI는 어떤 선택지가 있는지 알아야 도움말을 만들 수 있습니다. 반대로 Command가 `CsvStore` 같은 인프라를 아는 것은 계층 침범입니다.

### 3.7 형식 검증 함수 분리 (`_parse_*` / `_get_*` → `arg_types.py`)

- 처음에는 `AddCommand` 안에 `_parse_date`(변환, `@staticmethod`)와 `_get_date`(대화형 루프, 인스턴스 메서드)가 나뉘어 있었습니다. `_parse_*`는 `self`를 안 쓰는 순수 변환 함수라 static, `_get_*`는 상태나 `input()` 부수효과가 있어 인스턴스 메서드였습니다.
- 두 개로 나눈 이유: `--date`가 주어지면 argparse가 `type=parse_date`로 즉시 검증·변환하고(오류 시 표준 `error: argument --date: ...`), 주어지지 않으면 대화형 루프가 **같은 함수**로 검증합니다.
- **최종**: 여러 명령이 같은 검증을 쓰게 되어 `commands/arg_types.py`의 모듈 함수(`parse_date`, `parse_month`, `parse_type`, `parse_positive_int`)와 공용 재입력 헬퍼 `ask(label, parse)`로 옮겼습니다.
- `date.fromisoformat`은 3.11부터 `20240115`, `2024-W03-1`도 받아들입니다. 그래서 `models/period.py`의 `parse_date`가 정규식으로 `YYYY-MM-DD`를 먼저 고정합니다. 월(`YYYY-MM`) 규칙도 4곳(Budget, CLI, TransactionQuery, MonthlySummary)에 흩어져 있던 것을 같은 모듈의 `Month` 값 객체로 모았고, CLI는 이를 감싸서 argparse 오류로 바꾸기만 합니다.

### 3.8 네이밍: `base.py` + `BaseCommand`

| 옵션 | 경로 / 이름 | 평가 |
| --- | --- | --- |
| **채택** | `commands/base.py` + `BaseCommand` | Django(`django.core.management.base.BaseCommand`)와 같은 관례. 상속용 뼈대임이 이름에 드러남 |
| | `commands/base.py` + `Command` | 구체 클래스와 구분이 약함 |
| | `commands/base_command.py` | `commands.base_command.BaseCommand` — 단어 중복(stuttering) |

- `BaseRepository`, `BaseStore`도 같은 규칙으로 맞췄습니다.
- 하위 호환 별칭(`Command = BaseCommand`, `JsonTransactionRepository = ...`)은 필요 없으므로 **삭제**했습니다.

### 3.9 `name`/`help`가 `@property @abstractmethod`인 이유

- 값은 상수에 가깝지만 **서브클래스가 반드시 구현해야 하는 규약**입니다.
- 클래스 변수(`name: str`)는 빠뜨려도 에러가 나지 않습니다. 일반 `@abstractmethod`는 `cmd.name()`처럼 호출해야 해서 어색합니다.
- `@property @abstractmethod`는 구현을 강제하면서(빠뜨리면 인스턴스 생성 시 `TypeError`), `cmd.name`처럼 속성으로 읽힙니다.

### 3.10 의존성 주입: 왜 생성자로 받나?

- 주된 목적은 **테스트**입니다. 실제 파일 없이 Mock UseCase를 넣어 Command만 검증할 수 있습니다. CLI는 "실행 → 명령 1개 → 종료"라서 객체 재활용 이점은 거의 없습니다.
- 변천
  1. `AddCommand(service=None)`에서 `service or TransactionService()`로 기본값을 생성했습니다. 경로가 하드코딩돼 `--data-dir`을 반영할 수 없었습니다.
  2. 모든 Command가 `Container` 통째를 받았습니다. 어떤 UseCase에 의존하는지 생성자만 봐서는 알 수 없는 Service Locator 형태였습니다.
  3. **최종**: `bootstrap.build_commands(data_dir)`가 Store → Repository → UseCase → Command를 한 곳에서 조립하고, 각 Command는 **필요한 UseCase만** 생성자로 받습니다. Store는 처음 읽고 쓸 때 파일을 만들므로, 전부 미리 조립해도 `--help`는 파일을 건드리지 않습니다.

- **이름**: 처음엔 `container.py`였지만, Spring 같은 DI 컨테이너(등록 · 캐싱 · 자동 주입)가 아니라 시작할 때 한 번 조립하는 함수 하나라서 `bootstrap.py`로 바꿨습니다.
- **패키지 단위 import**: 조립 코드가 클래스 30개를 한 줄씩 import하던 것을, 각 패키지의 `__init__.py`가 클래스를 다시 내보내도록(re-export) 바꾸고 `from . import commands, repositories, stores, usecases` 한 줄로 가져옵니다. `usecases.AddTransactionUseCase(...)`처럼 계층 이름이 앞에 붙어 어느 계층의 객체를 조립하는지 바로 보입니다. `from .usecases import *`는 어떤 이름이 들어오는지 숨겨서 쓰지 않습니다.

```python
from argparse import Namespace
from unittest.mock import MagicMock
from budget_app.commands.delete import DeleteCommand

def test_delete_command():
    delete_uc = MagicMock()                       # 실제 파일 I/O 없음
    DeleteCommand(delete_uc).execute(Namespace(id=" TX-000001 "))
    delete_uc.execute.assert_called_once_with("TX-000001")
```

### 3.11 Service끼리 호출해도 되나? → UseCase 도입

- `TransactionService → CategoryService`처럼 단방향이면 당장은 문제없습니다. 하지만 서비스가 늘면 의존 그래프가 복잡해지고 순환(`A → B → A`)이 생기기 쉽습니다.
- 해결책은 여러 도메인을 조율하는 **UseCase 계층**입니다.
- **Spring에는 왜 UseCase가 없나?** Spring은 Controller → Service → Repository의 전통적인 레이어드 아키텍처를 따르고, `@Service`가 조율(UseCase)과 비즈니스 로직을 함께 맡는 넓은 의미로 설계됐습니다. 규모가 커지면 Spring에서도 ApplicationService/Facade나 헥사고날 아키텍처로 UseCase를 명시합니다. UseCase는 클린 아키텍처에서 나온 개념이고, 어느 쪽이 틀린 게 아니라 전제가 다른 것입니다.

### 3.12 UseCase만 쓰고 Service 계층은 두지 않는다

- UseCase가 Repository를 직접 호출하는 것은 클린 아키텍처의 기본 형태입니다.
- UseCase를 추가한 뒤의 `CategoryService`는 메서드 전부가 repo 호출(조회/저장)뿐이었습니다. 도메인 규칙이 없는 **Application Service**였고, UseCase와 역할이 겹쳤습니다. `BudgetService`도 같았습니다.
- **최종**: 애플리케이션 계층은 **"사용자 동작 1개 = UseCase 1개"**로만 구성하고, `services/`는 제거했습니다. 여러 UseCase가 쓰는 카테고리 존재 검증은 `usecases/category_guard.py`의 함수로 공유합니다.

#### Application Service(UseCase) vs Domain Service 구분

| | Application Service (= UseCase) | Domain Service |
| --- | --- | --- |
| 하는 일 | 불러오기 → 도메인에 맡기기 → 저장 (흐름 조율) | 비즈니스 규칙/계산 |
| repo 호출 | 함 | 안 함 (엔티티를 인자로 받음) |
| 이름 | 사용자 동작 (`AddTransaction`) | 도메인 개념 (`...Calculator`, `...Policy`) |
| 테스트 | 가짜 repo 필요 | 값만 넣어 바로 |

판별 질문: **"repo/파일/입출력을 몰라도 이 로직을 설명할 수 있나?"** → 설명할 수 있으면 도메인, 없으면 애플리케이션입니다.

#### 규칙 배치 순서

1. 엔티티/값 객체 하나로 판단 가능하면 **모델 안**에 둡니다 (빈 카테고리명 → `Category`, 금액 양수 → `Transaction.create`, 예산 사용률 → `Budget.evaluate(spent)`).
2. 여러 엔티티에 걸쳐 어느 한쪽에 두기 애매하면 **Domain Service**로 뺍니다 (현재 해당 없음. 예산 계산도 `Budget` + 지출액이면 충분해서 엔티티 메서드가 됨).
3. 저장소에 물어봐야 알면 **UseCase**에서 처리합니다 (카테고리 존재, id 존재, 중복 등록).

처음부터 Domain Service로 빼면 엔티티는 데이터만 담는 껍데기가 되고(빈약한 도메인 모델), 규칙이 서비스로 흩어집니다.

### 3.13 도메인 리치 모델과 정적 팩토리

- 검증을 UseCase가 아니라 모델로 옮겼습니다.
- `Transaction.__post_init__`과 `Transaction.create()`의 역할을 나눴습니다.

| | 역할 | 호출 시점 |
| --- | --- | --- |
| `Transaction.__post_init__` | **타입 변환만** (str → date/Enum/list) | 모든 생성 — Repository 역직렬화 포함 |
| `Transaction.create()` | **비즈니스 검증 + 정규화** 후 생성 (금액 양수, 카테고리 비어있지 않음, 메모 정리) | 새 거래를 만들 때 (add, update, import) |

- 저장된 데이터를 다시 읽을 때 검증 규칙이 바뀌었다고 읽기가 실패하면 안 되므로, 역직렬화에는 변환만 적용합니다.
- 카테고리 **존재 여부**는 저장소 조회가 필요하므로 모델로 옮기지 않고 UseCase에 남겼습니다. 모델은 Repository를 몰라야 합니다.
- 카테고리 정규화 규칙(공백 제거 + 소문자)은 `Category.normalize_name()` 한 곳에 두고, Command·UseCase·Repository가 재사용합니다.

### 3.14 ID 채번은 어디서?

- 변천
  1. Service가 `find_all()`로 전체를 읽어 정규식으로 최대값을 찾았습니다. 저장소 세부 사항에 결합돼 있고, 데이터가 많아지면 느려집니다.
  2. `TransactionRepository.next_id()`로 이동했습니다. ID 발급(시퀀스/auto increment)은 영속성 계층의 책임이기 때문입니다.
  3. `next_id()`를 UseCase가 부르는 것도 인프라 디테일이 새는 것이라, `Repository.save()` 내부에서 id가 비어 있으면 채번하도록 바꿨습니다. `Transaction.create()`는 id 없이 만들고, `dataclasses.replace(tx, id=...)`로 채웁니다.
  4. **최종**: "파일에 남은 최대값 + 1"로 채번하면 마지막 거래를 삭제했을 때 같은 id가 재발급됩니다. 그래서 마지막 발급 번호를 `transactions.seq`에 기록하고, `max(시퀀스, 실제 최대값) + 1`로 발급합니다.

### 3.15 데이터 안전성

- 기존 `CsvStore.load()`는 읽기 오류 시 `[]`를 반환했습니다. 그 상태로 저장하면 **파일 전체가 지워질 수 있었습니다**. 이제는 오류를 그대로 올려 `[오류]` 메시지로 보여줍니다.
- 전체 재작성은 임시 파일에 쓴 뒤 `os.replace`로 교체합니다. 같은 파티션 안의 rename은 원자적이라, 중간에 실패해도 원본 아니면 새 파일 둘 중 하나만 존재합니다.
- 카테고리 삭제 시 거래 이동을 먼저 끝내고 카테고리를 지웁니다. 중간에 실패해도 "존재하지 않는 카테고리를 가진 거래"가 남지 않습니다.

### 3.16 예외 처리와 린트 경고

- `@handle_errors`(`cli.main`에 적용)가 예외 종류별로 `[오류] 원인` + `[힌트] 해결 방법`을 출력하고 종료 코드를 정합니다. 각 계층은 `raise`만 하면 됩니다.
  - `BudgetAppError` 하위 예외: `hint_for()`가 예외 종류별 CLI 안내를 붙임
  - `ValueError`: 모델 검증 실패
  - `OSError`: 파일 경로/권한
  - `KeyboardInterrupt`: `[취소]` + 130
- **원인과 안내의 분리**: 처음에는 UseCase가 `hint="'python -m budget_app category add --name ...'"`처럼 CLI 명령과 옵션 이름을 직접 들고 있었습니다. UseCase가 CLI를 알면 옵션 이름을 바꿀 때 UseCase까지 고쳐야 하고, 다른 UI를 붙이면 엉뚱한 안내가 나갑니다.
  - **최종**: UseCase는 `CategoryNotFoundError(name, available)`, `CategoryInUseError(name, count)`, `TransactionNotFoundError(id)`처럼 **무엇이 잘못됐는지**만 데이터로 담아 던집니다. **어떻게 고치는지**는 `commands/error_handler.py`의 `hint_for()` 한 곳이 붙입니다.
  - CLI 옵션 조합 오류(`export`의 `--month`와 `--from` 동시 사용)는 CLI에서만 생기므로 `UsageError`가 힌트를 직접 가집니다.
  - `tests/`의 구조 테스트가 models/repositories/stores/usecases에 CLI 명령이나 `--옵션` 문자열이 들어가면 실패합니다.
- **argparse 오류**: argparse는 기본적으로 `error: ...` 영어 한 줄만 출력해서 다른 오류와 형식이 달랐습니다. `cli.py`의 `HintArgumentParser`가 `error()`를 재정의해 `[오류]`/`[힌트]` 형식으로 맞춥니다. 하위 명령 파서도 이 클래스를 그대로 물려받습니다.
- **`BLE001` (blind except)**: `except Exception`은 버그를 삼키므로 보통 피해야 합니다. 하지만 CLI 최상단 진입점에서 스택트레이스 대신 안내를 출력하는 것은 일반적인 관례라서 `# noqa: BLE001`로 의도를 명시했습니다. `--verbose`로 실행하면 상세 로그가 출력됩니다.
- **`UP007`**: `Optional[X]` 대신 Python 3.10+ 문법 `X | None`을 씁니다.
- **`Redefinition of unused 'save'`**: 같은 클래스에 같은 이름의 메서드가 두 번 정의되면 나는 경고입니다. 하나를 지웁니다.

### 3.17 로직 위치 재검토

기능이 다 갖춰진 뒤 "이 코드가 이 계층에 있는 게 맞나"를 기준으로 다시 정리했습니다.

| 로직 | 이전 위치 | 최종 위치 | 이유 |
| --- | --- | --- | --- |
| 오류 해결 안내 (CLI 명령/옵션) | UseCase의 `hint=` | `commands/error_handler.py` `hint_for()` | UseCase는 CLI를 몰라야 함 (3.16) |
| CSV 스키마, 헤더 검증, 행 ↔ Transaction 변환 | import/export UseCase | `repositories/transaction_csv.py` (주입) | 파일 형식 처리는 영속성 쪽 책임. export의 변환 코드가 Repository `_to_dict`와 중복돼 있었음 |
| 날짜/월 형식 규칙 | Budget, CLI, TransactionQuery, MonthlySummary, Transaction | `models/period.py` (`Month` 값 객체) | 같은 정규식이 여러 곳에 복사돼 있었음 |
| 예산 id 형식 (`"2024-01:all"`) | `GetMonthlySummaryUseCase`가 직접 조립 | `BudgetRepository.find_by_month()` | 저장 키 형식은 Repository만 알면 됨 |
| 최신순 정렬 키 | `list_transactions.py` (search가 import) | `Transaction.recency_key()` | 정렬 기준은 도메인 규칙. UseCase끼리 의존하던 것도 해소 |
| 테이블/금액 출력 | `budget_app/formatters.py` | `commands/formatters.py` | Command만 쓰는 출력 코드 |
| `@handle_errors` | `decorators.py` | `commands/error_handler.py` | `print`/`sys.exit`/CLI 안내 — CLI 전용. 범용 `@log_execution`만 `decorators.py`에 남김 |
| tags 문자열 파싱 | Repository `_to_entity` + Transaction | `Transaction.__post_init__`만 | 중복 제거 |
| `TransactionCsvFile` | (처음에 `stores/`에 둠) | `repositories/` | Store는 도메인 객체를 모름. Transaction 변환을 하므로 Repository 계층 |
| `json_store.py` | `stores/` | 삭제 | `BaseStore`를 구현하지 않고 쓰는 곳도 없음 |

그대로 둔 것:
- `export`의 "`--month` 또는 `--from/--to` 필수" 규칙 → 옵션 조합이므로 Command
- `AddCommand`의 카테고리 사전 확인 → 대화형 재입력 UX. 최종 검증은 UseCase가 다시 함
- `usecases/category_guard.py` → 여러 UseCase가 쓰는 "저장소 조회가 필요한 검증"

#### 계층별 헬퍼를 `utils/`로 모으지 않은 이유

`period.py`, `csv_file.py`, `transaction_csv.py`가 "곳곳에 퍼진 util"처럼 보일 수 있지만, 각자 자기 계층 안에 있는 **계층별 헬퍼**이고 성격이 다릅니다.

| 파일 | 계층 | 성격 | 쓰는 곳 |
| --- | --- | --- | --- |
| `models/period.py` | 도메인 | 도메인 규칙 — "유효한 날짜/월이란". `Month` 값 객체 | Transaction, Budget, TransactionQuery, MonthlySummary, CLI |
| `stores/csv_file.py` | 인프라 | 계층 내부 헬퍼 — CSV 스트리밍 읽기, 원자적 쓰기 | CsvStore, TransactionCsvFile |
| `repositories/transaction_csv.py` | 영속화 | util이 아닌 **주입되는 어댑터** (스키마를 가진 클래스) | import/export UseCase |

- `utils.py`라는 이름은 안에 무엇이 들었는지 숨기고, "어디 둘지 애매한 코드"가 모이면서 계층 경계를 다시 흐립니다. 그래서 역할이 드러나는 이름을 씁니다.
- `period.py`는 처음엔 함수 묶음(`parse_month`, `month_of`, `month_range`)이라 util처럼 보였습니다. **`Month` 값 객체**로 바꿔 `Budget.month`, `MonthlySummary.month`, CLI `--month`가 모두 문자열이 아니라 검증된 `Month` 타입을 주고받습니다. 저장할 때만 `str(month)` → `"2024-01"`로 직렬화합니다.

```python
Month.parse("2024-02")          # 검증 (형식 오류면 ValueError)
Month.of(tx.date)               # 날짜 → 월
month.first_day, month.last_day # 2024-02-01, 2024-02-29 (윤년 반영)
```

계층 의존 방향(models → 아무것도 모름, stores → 도메인 모름, usecases → CLI/stores 모름)은 `tests/test_integration.py`의 `ArchitectureTest`가 import를 분석해 검사합니다.

### 3.18 Python 버전

- `typing.override`(3.12+)를 쓰므로 **Python 3.12 이상**이 필요합니다. 미션 조건 "3.10 이상"은 만족하며, 오버라이드 오타를 정적 분석기가 잡아주는 이점 때문에 유지합니다.

---

## 4. 핵심 개념 정리

### `argparse`

터미널 입력(`add --amount 5000`)을 파싱하는 표준 라이브러리입니다.

- `add_subparsers()`: 하위 명령 (`add`, `list`, `category add` ...)
- `type=함수`: 인자를 변환·검증합니다. `ArgumentTypeError`를 던지면 argparse가 표준 에러 메시지로 출력하고 종료 코드 2로 끝냅니다.
- `set_defaults(handler=...)`: 하위 명령별 실행 함수를 연결합니다 (`budget set/show`, `category add/list/remove`).
- `parse_known_args()`: 일부 옵션(`--data-dir`)만 먼저 읽습니다. 의존성 조립에 필요합니다.

### `@override` (Python 3.12+)

```python
from typing import override

class CsvStore(BaseStore):
    @override
    def stream(self): ...
```

자식에서 같은 이름으로 정의하면 자동으로 오버라이드되지만, `@override`를 붙이면 부모에 그 메서드가 실제로 있는지 정적 분석기가 검증합니다 (Java `@Override`와 같은 역할, 오타 방지).

### `@dataclass`

`__init__`, `__repr__`, `__eq__`를 자동 생성합니다.

- `field(default_factory=list)`: 가변 기본값을 인스턴스마다 새로 생성합니다 (`tags`)
- `frozen=True`: 불변 객체 (`BudgetStatus`, `TransactionQuery`, 결과 객체)
- `__post_init__`: 생성 직후 변환/검증
- `dataclasses.replace(obj, field=...)`: 일부 필드만 바꾼 사본을 만듭니다 (id 채번, 카테고리 이동)

### `Enum` / `StrEnum`

```python
from enum import StrEnum, auto

class TransactionType(StrEnum):
    INCOME = auto()    # "income"
    EXPENSE = auto()   # "expense"
```

`StrEnum`(3.11+)은 `auto()`가 소문자 이름 문자열이 되어 직렬화와 출력에 유리합니다. `TransactionType("expense")`로 문자열에서 변환하고, 잘못된 값이면 `ValueError`가 납니다.

### 날짜 타입

`datetime.date`를 쓰고, 문자열은 `date.fromisoformat("2024-01-15")`로 변환합니다. `fromisoformat`이 3.11부터 다른 ISO 형식도 받아들이므로 `re.fullmatch(r"\d{4}-\d{2}-\d{2}", s)`로 형식을 먼저 강제합니다. `2024-02-30`처럼 존재하지 않는 날짜는 `fromisoformat`이 거부합니다.

제너레이터, 데코레이터, 타입 힌트는 과제 목표와 직접 연결되므로 [5장](#5-과제-목표별-설명)에서 설명합니다.

---

## 5. 과제 목표별 설명

### 5.1 파일 기반 영구 저장과 CRUD · 검색 · 요약 · 입출력

데이터는 `transactions.csv` / `categories.csv` / `budgets.csv` 3개 파일(+ id 순번 `transactions.seq`)에 나눠 저장합니다. 기능마다 파일을 다루는 방식이 다릅니다.

| 기능 | 명령 | 흐름 | 파일 처리 |
| --- | --- | --- | --- |
| **Create** | `add`, `import` | `Transaction.create()` 검증 → `repo.save()`가 id 채번 | `add`: 파일 끝에 **append** (O(1)). `import`: 통과한 행을 모아 **한 번에 원자적 재작성** |
| **Read** | `list`, `search` | `repo.stream()` → 필터 → 최신순 | **스트리밍 읽기**. 결과(최대 N건)만 메모리에 |
| **Update** | `update` | `find_by_id()` → 바뀐 필드만 합쳐 `Transaction.create()`로 재검증 → `save()` | 원본을 스트리밍으로 읽으며 해당 행만 바꿔 **임시 파일에 쓰고 `os.replace`** |
| **Delete** | `delete` | 존재 확인 → 해당 행 제외 | 위와 같은 스트리밍 재작성 + 원자적 교체 |
| 요약 | `summary`, `budget show` | `MonthlySummary.from_transactions(stream)` + `Budget.evaluate(spent)` | 스트리밍으로 합계만 누적 |
| 입출력 | `import`, `export` | `TransactionCsvFile`이 스키마 검증 · 행 변환 | `export`는 읽는 즉시 출력 파일에 기록 |

- **왜 원자적 교체인가**: 파일을 직접 덮어쓰다 중간에 실패하면 반쯤 쓰인 파일이 남습니다. 임시 파일에 다 쓴 뒤 `os.replace`(같은 폴더 안 rename은 원자적)로 바꾸면, 원본 아니면 새 파일 둘 중 하나만 존재합니다.
- **왜 파일을 나눴나**: 엔티티마다 Repository가 하나의 파일만 책임져서, 한 파일이 손상돼도 다른 데이터는 영향을 받지 않고 형식(컬럼)도 각자 관리됩니다.

### 5.2 계층 구조와 책임 (모델 / 저장소 / 서비스 / CLI)

| 과제 용어 | 이 프로젝트 | 책임 |
| --- | --- | --- |
| CLI | `cli.py`, `commands/` | 인자 파싱, 형식 검증, 대화형 입력, 출력, 오류 안내 |
| 서비스 | `usecases/` | 사용자 동작 1개의 흐름 조율 (가져오기 → 도메인에 맡기기 → 저장). "서비스"를 동작 단위로 나눈 것 ([3.12](#312-usecase만-쓰고-service-계층은-두지-않는다)) |
| 모델 | `models/` | 데이터와 규칙 (금액 양수, 예산 사용률, 월 계산, 검색 조건) |
| 저장소 | `repositories/` + `stores/` | 도메인 객체 ↔ dict 변환(Repository), 실제 파일 I/O(Store) |

`python -m budget_app add --date 2024-01-15 --type expense --category food --amount 15000 ...` 한 번이 거치는 경로:

```text
cli.main()                 @handle_errors로 감쌈. --data-dir 읽고 bootstrap으로 조립
 └ AddCommand.execute()    argparse가 --date/--amount를 이미 date/int로 변환. 빠진 값은 input()으로
    └ AddTransactionUseCase.execute()
       ├ ensure_category_exists()        카테고리 등록 여부 (저장소 조회 → UseCase 책임)
       ├ Transaction.create()            금액 양수, 카테고리 정규화 (모델 책임)
       └ StoreTransactionRepository.save()   id 채번 + Transaction → dict
          └ CsvStore.append()            파일 끝에 한 줄 기록
 ← "[저장 완료] id=TX-000001"           출력은 다시 Command가
```

### 5.3 제너레이터(`yield`)로 스트리밍 처리

**왜**: 파일 전체를 `list`로 읽으면 메모리가 파일 크기만큼 필요합니다. 제너레이터는 한 번에 한 행만 메모리에 두므로 파일이 커져도 사용량이 일정합니다. `tests/`의 `StreamingTest`가 5만 건에서 `list --limit 10`의 최대 메모리가 전체 로드 대비 1/10 미만인지 검사합니다.

**동작 방식**

```python
# stores/csv_file.py
def read_csv_rows(filepath):
    with open(filepath, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            yield dict(row)

# repositories/transaction.py
def stream(self) -> Iterator[Transaction]:
    for item in self._store.stream():
        yield self._to_entity(item)

# usecases/list_transactions.py
heapq.nlargest(limit, self._tx_repo.stream(), key=Transaction.recency_key)
```

1. `yield`가 있는 함수는 호출해도 **본문이 실행되지 않고** 제너레이터 객체만 반환합니다.
2. 소비하는 쪽(`for`, `heapq.nlargest`)이 다음 값을 요청하면 그때 실행되어, `yield`에서 값을 넘기고 **멈춥니다**. 지역 변수와 열린 파일 상태는 그대로 유지됩니다.
3. 다시 요청하면 멈춘 지점부터 이어서 실행합니다. 끝까지 가면 `with` 블록이 끝나면서 파일이 닫힙니다.
4. 여러 제너레이터를 연결하면 **한 행이 파이프라인 전체를 통과한 뒤** 다음 행을 읽습니다 (파일 → dict → Transaction → 필터 → heap).

**주의점**
- **한 번만 순회 가능**: 다 쓴 제너레이터는 다시 돌릴 수 없습니다. 두 번 필요하면 `stream()`을 다시 호출합니다.
- **지연 실행 함정**: 제너레이터 함수 안의 검증은 첫 `next()` 때 실행됩니다. 그래서 `TransactionCsvFile.read()`는 파일 존재와 헤더를 **먼저 검사한 뒤** 행 제너레이터를 반환하도록 일반 함수로 감쌌습니다.
- **정렬과의 조화**: 최신순은 끝까지 봐야 알 수 있습니다. 전체를 정렬하는 대신 `heapq.nlargest(N, ...)`로 N건만 유지해, 스트리밍을 지키면서 메모리를 결과 크기로 제한합니다.

### 5.4 데코레이터로 공통 관심사 분리

**동작 방식**: `@deco`는 문법 설탕입니다. 아래 두 코드는 같습니다.

```python
@log_execution
def execute(self, args): ...

def execute(self, args): ...
execute = log_execution(execute)   # 원래 함수를 받아 감싼 새 함수(wrapper)로 교체
```

```python
# decorators.py
def log_execution(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)                 # 원래 함수 이름/docstring 보존
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.info("%s 시작", func.__qualname__)
        started = time.perf_counter()
        try:
            return func(*args, **kwargs)   # 원래 함수 실행
        finally:                           # 성공/실패와 무관하게 시간 기록
            logger.info("%s 종료 (%.3fs)", func.__qualname__, time.perf_counter() - started)
    return wrapper
```

| 데코레이터 | 공통 관심사 | 적용 위치 |
| --- | --- | --- |
| `@handle_errors` (`commands/error_handler.py`) | **예외 처리**: 예외 종류별 `[오류]` + `[힌트]`, 종료 코드(0/1/130) | `cli.main` 한 곳 |
| `@log_execution` (`decorators.py`) | **실행 로그 + 시간 측정** (`--verbose` 시 출력) | 모든 `Command.execute` |

**왜**: 데코레이터가 없으면 명령 10개마다 같은 코드가 반복되고, 본래 로직이 부가 코드에 묻힙니다.

```python
# 데코레이터 없이
def execute(self, args):
    started = time.perf_counter()
    try:
        ...  # 실제 로직
    except NotFoundError as e:
        print(f"[오류] {e}"); sys.exit(1)
    finally:
        logger.info("... (%.3fs)", time.perf_counter() - started)

# 데코레이터 사용 — 실제 로직만 남음
@log_execution
def execute(self, args):
    ...
```

- 데코레이터를 여러 개 쓰면 아래(함수에 가까운 쪽)부터 감쌉니다. Command 코드처럼 `@override` 아래에 `@log_execution`이 있으면 `override(log_execution(execute))` 순서입니다.

### 5.5 타입 힌트로 입출력 계약 명시

타입 힌트는 실행 시 강제되지 않지만, IDE와 정적 분석기(pyright/mypy)가 호출 전에 실수를 잡아 주고 **함수만 보고도 무엇을 주고받는지** 알 수 있게 합니다.

**① 문자열 대신 도메인 타입 — `Month`**

```python
# 이전: 아무 문자열이나 들어올 수 있음. 검증을 호출하는 쪽마다 반복
def execute(self, month: str) -> MonthlyReport: ...
usecase.execute("2024-1")      # 잘못된 형식이 그대로 통과

# 지금: '검증된 월'만 받는다는 계약
def execute(self, month: Month) -> MonthlyReport: ...
usecase.execute(Month.parse("2024-01"))
usecase.execute("2024-01")     # IDE가 타입 불일치로 경고
```

**② `| None` — 없을 수 있음을 강제로 처리**

```python
def find_by_id(self, entity_id: str) -> Transaction | None: ...

current = self._tx_repo.find_by_id(tx_id)
current.amount                 # 정적 분석기: "None일 수 있음" 경고
if current is None:
    raise TransactionNotFoundError(tx_id)
current.amount                 # 여기서부터는 Transaction으로 확정
```

**③ 추상 타입으로 받기 — 교체 가능한 계약**

```python
class AddTransactionUseCase:
    def __init__(self, tx_repo: TransactionRepository, category_repo: CategoryRepository): ...
```

구현체(`StoreTransactionRepository`)가 아니라 인터페이스 타입을 받으므로, 저장 방식을 바꾸거나 테스트에서 가짜 객체를 넣어도 UseCase 코드는 그대로입니다 ([3.10 테스트 예](#310-의존성-주입-왜-생성자로-받나)).

**④ 제너레이터 · 데코레이터의 계약**

```python
def stream(self) -> Iterator[Transaction]: ...                   # 한 번만 순회하는 스트림
def log_execution(func: Callable[P, R]) -> Callable[P, R]: ...  # 감싼 뒤에도 원래 시그니처 유지
```

`ParamSpec(P)`가 없으면 데코레이터를 거친 함수는 `(...) -> Any`가 되어 인자 자동완성과 검사가 사라집니다.

**⑤ 그 밖의 예**
- `BaseRepository(ABC, Generic[T])`: `TransactionRepository`는 `save(Transaction) -> Transaction`, `CategoryRepository`는 `save(Category) -> Category`로 같은 인터페이스를 타입만 바꿔 재사용합니다.
- `TransactionType` (StrEnum): `type_val: TransactionType`이면 `"expens"` 같은 오타 문자열이 들어갈 자리가 없습니다.
- `@override`: 부모에 없는 메서드를 오버라이드한다고 표시하면(오타) 정적 분석기가 오류를 냅니다.
