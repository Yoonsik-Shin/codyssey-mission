# MAC 연산 (E1/3) — Mini NPU 시뮬레이터

3×3 ~ 25×25 필터/패턴 매트릭스의 Multiply-Accumulate(MAC) 연산으로 Cross/X 패턴을 판별하는 콘솔 프로그램.

## 실행 방법

```bash
python main.py
```

실행하면 모드 선택 프롬프트가 뜬다.

- `1` : 사용자 입력 모드. 3×3 필터 A, B, 패턴을 한 줄씩(공백 구분 숫자 3개) 입력받아 MAC 점수/판정/연산시간을 출력한다.
- `2` : data.json 분석 모드. 스크립트와 같은 폴더의 `data.json`(`E1/3/data.json`)을 읽어 size_5/13/25 필터로 6개 패턴을 일괄 판정하고, 성능 분석과 결과 요약을 출력한다.

`1`/`2` 외 값이나 숫자가 아닌 값을 입력하면 재입력을 유도한다. 사용자 입력 모드에서 행의 숫자 개수가 3개가 아니거나 파싱이 안 되면 같은 줄을 다시 입력받는다.

보너스 과제는 `main.py`와 별도 파일로 분리되어 있다.

```bash
python bonus/bonus2_generator.py   # 보너스2: N 크기 Cross/X 패턴 자동 생성 + 판정 시연
python bonus/bonus1_optimize.py    # 보너스1: 2D vs 1D vs O(2N-1) 희소 MAC 연산 성능 비교
```

## 구현 요약

- **모듈 구조**: `main.py`는 모드 선택 진입점 역할만 하고, 실제 로직은 책임별로 분리되어 있다.
  - [mac_calculator.py](file:///Users/aaa9460994/Desktop/codyssey-mission/E1/3/mac_calculator.py) → `MacCalculator`: MAC 연산(`calculate_2d`), 판정(`judge`), 동점 비교(`_is_same_value`)
  - [label_normalizer.py](file:///Users/aaa9460994/Desktop/codyssey-mission/E1/3/label_normalizer.py) → `LabelNormalizer`: 라벨 정규화(`normalize`)
  - [utils/matrix_utils.py](file:///Users/aaa9460994/Desktop/codyssey-mission/E1/3/utils/matrix_utils.py) → `MatrixUtils`: 셀 단위 읽기/쓰기(`get_cell`/`set_cell`)
  - [utils/input_utils.py](file:///Users/aaa9460994/Desktop/codyssey-mission/E1/3/utils/input_utils.py) → `InputUtils`: 사용자 입력 검증/파싱(`input_matrix`)
  - [utils/output_utils.py](file:///Users/aaa9460994/Desktop/codyssey-mission/E1/3/utils/output_utils.py) → `OutputUtils`: 여러 줄을 한 번에 출력(`print_lines`)
  - [mode/user_input_mode.py](file:///Users/aaa9460994/Desktop/codyssey-mission/E1/3/mode/user_input_mode.py), [mode/json_input_mode.py](file:///Users/aaa9460994/Desktop/codyssey-mission/E1/3/mode/json_input_mode.py): 모드별 실행 흐름
- **MAC 연산**: `MacCalculator.calculate_2d`. 외부 라이브러리 없이 이중 반복문으로 같은 위치 값끼리 곱해서 누적.
- **판정 로직**: `MacCalculator.judge(score_a, label_a, score_b, label_b)`. 두 점수를 직접 비교해서 큰 쪽 라벨을 반환하고, `|score_a - score_b| < 1e-9`(epsilon)면 `UNDECIDED`를 반환한다. 사용자 입력 모드(A/B)와 JSON 모드(Cross/X)가 이 함수 하나를 공유한다.
- **라벨 정규화**: `LabelNormalizer.normalize(raw)`. `'+'`/`'cross'` → `Cross`, `'x'` → `X` 로 표준화. filter 키와 `expected` 값 양쪽 다 이 함수를 거쳐 표준 라벨(Cross/X)로만 비교/출력한다.
- **동점 처리 정책**: 위 epsilon 기준(`1e-9`)을 전역으로 통일해서 사용. 점수가 부동소수점 연산 결과라 정확히 같은 값이 아니어도 근접하면 동점으로 간주해야 하기 때문.
- **모드별 동점 규칙 차이**: 판정 로직(`MacCalculator.judge`, epsilon 1e-9)은 모드1/모드2가 완전히 동일하다. 차이는 UNDECIDED 결과를 어떻게 소비하느냐에 있다. 모드1은 `expected` 값이 없는 순수 비교 모드라 UNDECIDED가 나와도 "판정 불가" 안내만 하고 끝난다(PASS/FAIL 개념 자체가 없음). 모드2는 `expected`(Cross 또는 X)가 정해져 있는 채점 모드라, UNDECIDED는 Cross·X 어느 쪽과도 일치할 수 없는 값이므로 항상 FAIL로 집계된다.
- **데이터 접근**: `MatrixUtils.get_cell`/`MatrixUtils.set_cell`로 매트릭스 특정 위치 값을 읽고 쓴다.
- **스키마 방어**: JSON 모드에서 패턴 키(`size_{N}_{idx}`)로부터 N을 추출해 대응하는 `size_N` 필터를 찾고, 필터/패턴 크기가 일치하는지 검증한다. 필터가 없거나 크기가 안 맞으면 예외를 던지지 않고 해당 케이스만 FAIL 처리하고 다음 케이스로 넘어간다.

## 결과 리포트

`python main.py` → 모드 `2` 실행 결과(2026-08-17 기준, `mac_calculator.py`/`utils/`/`mode/` 모듈 분리 리팩터링 이후 재검증, data.json 원본 그대로):

```text
총 테스트: 6개
통과: 3개
실패: 3개

- size_5_1:  Cross=0.9,                X=0.8999999999999999   → UNDECIDED (FAIL)
- size_13_2: Cross=7.499999999999997,  X=7.5                  → UNDECIDED (FAIL)
- size_25_1: Cross=4.9,                X=4.899999999999999    → UNDECIDED (FAIL)
```

**실패 원인 분석**: 3개 실패 케이스 모두 "동점 규칙"에 의한 FAIL이고, 스키마/키 문제나 로직 버그가 아니다. data.json의 필터 값을 보면 십자가/X 모양의 중심축은 정확히 1.0이 아니라 0.9, 0.3, 4.9, 7.5 같은 근사값으로 일부러 채워져 있다. 예를 들어 size_5_1은 Cross 필터 중심이 0.9라서 패턴과 곱했을 때 Cross 점수가 정확히 0.9가 나오고, X 필터는 대각선 8칸이 각각 0.1이라 X 점수가 0.8999999999999999(부동소수점 덧셈 오차 포함)가 된다. 두 값의 차이는 1e-16 수준이라 `abs(a-b) < 1e-9` 기준으로는 명백한 동점이다. 이건 "필터/패턴이 진짜로 구분이 안 되는 입력을 만들었을 때 프로그램이 UNDECIDED로 정직하게 답하는지" 테스트하기 위해 데이터셋 제작자가 의도적으로 넣은 케이스로 판단된다. 이전 구현은 필터 값을 로드 직후 0/1로 강제 변환(바이너리화)해서 이 근사값들이 전부 지워졌고, 그 결과 판정도 상수(`2n-1`) 비교라는 별개의 잘못된 로직으로 계산돼서 같은 UNDECIDED가 나와도 근거가 틀렸었다. 현재 구현은 필터 값을 원본 그대로 사용하고 점수를 직접 비교하므로, 실패가 나더라도 원인이 "동점 규칙" 하나로 명확하게 귀결된다. 반대로 size_13_1처럼 노이즈가 있어도 점수 차이가 충분히 크면(0.3 vs 14.7) 정상적으로 X 판정 후 PASS 처리된다. 즉 이번 3건의 FAIL은 데이터/스키마 문제도 로직 버그도 아니고, epsilon 비교 정책이 의도대로 동작한 결과다.

**시간복잡도(O(N²)) 분석**: `calculate_mac`은 N×N 매트릭스 두 개를 이중 for문으로 순회하며 각 위치에서 곱셈 1회, 누적 덧셈 1회를 수행한다. 즉 연산 횟수는 정확히 N²에 비례한다(3×3=9회, 5×5=25회, 13×13=169회, 25×25=625회). 실측 결과(10회 반복 평균)는 다음과 같이 이 비율을 그대로 따라간다:

```text
크기       평균 시간(ms)    연산 횟수
3×3            0.002            9
5×5            0.003           25
13×13          0.014          169
25×25          0.046          625
```

9 → 625로 연산 횟수가 약 70배 증가할 때 측정 시간도 0.002ms → 0.046ms로 약 20배 이상 증가해 대략 비례 관계를 보인다(작은 크기에서는 Python 함수 호출/루프 오버헤드 비중이 상대적으로 커서 정확히 70배까지는 안 나오지만, N이 커질수록 O(N²) 경향에 수렴한다). 실제 NPU가 수백×수백 필터 수천 개를 병렬 MAC 유닛으로 처리하는 이유도 여기 있다 — CPU가 이 반복문을 직렬로 돌리면 N이 커질수록 연산량이 제곱으로 늘어나 감당이 안 되기 때문이다.

## 보너스 과제

### 보너스1 — 시뮬레이터 최적화 (`bonus1_optimize.py`)

2차원 매트릭스를 길이 N²짜리 1차원 배열로 펼쳐서(`MatrixUtils.flatten`, row-major: `index = row*N + col`) 접근 패턴을 단순화했다. `MatrixUtils.set_cell_1d`/`get_cell_1d`로 셀 단위 읽기/쓰기를 하고, `MacCalculator.calculate_1d`는 중첩 for문 대신 단일 for문(`zip`)으로 곱셈-누적을 수행한다. 2D `MacCalculator.calculate_2d`와 동일 입력·동일 반복 횟수(10회, `timeit.repeat` 5세트 중 최솟값 채택으로 노이즈 억제)로 비교했다. 스펙 최소 요구 크기(3/5/13/25)에 더해 50~800까지 키워서 극적인 스케일 차이를 확인한 실측 결과:

```text
크기         2D(ms)     1D(ms)     개선율
--------------------------------------------
3x3          0.0009     0.0005     44.0%
5x5          0.0018     0.0010     42.9%
13x13        0.0075     0.0058     22.4%
25x25        0.0221     0.0197     10.8%
50x50        0.0829     0.0784      5.4%
100x100      0.3285     0.3117      5.1%
200x200      1.3122     1.2525      4.6%
400x400      5.0982     5.0307      1.3%
800x800     20.6122    20.3147      1.4%
```

절대 시간은 3×3(9회 연산) → 800×800(64만회 연산)까지 4자리수 이상 벌어져서 O(N²) 스케일 자체가 극적으로 드러난다. 다만 1D의 상대 개선율은 반대로 N이 커질수록 줄어든다(3×3에서 44% → 800×800에서 1%대). 이유: 2D 버전의 오버헤드는 "행(N)마다 `zip(f_row, p_row)` 이터레이터를 새로 만드는 비용"인데 이건 N에 비례해서만 늘고, 두 버전 다 공유하는 실제 곱셈-누적 비용은 N²에 비례해서 늘어난다. N이 커질수록 분모(N² 연산량)가 분자(N개 이터레이터 생성 오버헤드)보다 훨씬 빨리 커지므로 1D가 절대적으로는 계속 더 빠르지만 비율상 격차는 좁아진다 — 두 구현 모두 결국 같은 Python 레벨 곱셈-덧셈 N²회가 병목이기 때문이다.

#### 보너스1 추가 — Cross 패턴 희소성 활용 O(2N-1) 최적화

위 1D 최적화는 상수 인자(이터레이터 생성 오버헤드)만 줄일 뿐 여전히 N²회 곱셈-누적을 그대로 수행한다. 그런데 `generate_cross_pattern(n)`이 만드는 십자가 필터는 중심 행/열(`n//2`)에만 값이 있고 나머지 칸은 전부 0이라, 0이 아닌 칸은 정확히 `2n-1`개(중심 행 n개 + 중심 열 n개 − 겹치는 중심 칸 1개)뿐이다. 마찬가지로 `generate_x_pattern(n)`이 만드는 X 필터도 두 대각선 외 전부 0이라 0이 아닌 칸이 `2n-1`개(홀수 n 기준, 중심에서 두 대각선이 겹침)뿐이다. `MacCalculator.calculate_cross_sparse(filter_matrix, pattern_matrix, n)`/`calculate_x_sparse(filter_matrix, pattern_matrix, n)`는 이 사실을 이용해 나머지 칸은 아예 순회하지 않고 그 `2n-1`칸만 곱해서 더한다 — 시간복잡도가 O(N²)에서 O(2N-1), 즉 O(N)으로 낮아진다. 단, 이 최적화는 필터가 실제로 해당 모양(Cross는 중심 행/열, X는 두 대각선 외 전부 0)일 때만 유효하다는 전제가 있다 — 일반 필터에는 적용할 수 없다.

`verify_sparse_correctness()`로 Cross/X 각각 dense(O(N²)) 결과와 값이 정확히 일치하는지 먼저 검증한 뒤, `benchmark_compare_sparse()`로 기존 O(N²)와 비교한 실측 결과(평균/10회, `timeit.repeat` 5세트 중 최솟값):

```text
크기        패턴      O(N²)(ms)     O(2N-1)(ms)   개선율
--------------------------------------------------------
3x3      Cross   0.0017        0.0013          24.2%
3x3      X       0.0017        0.0014          19.6%
5x5      Cross   0.0032        0.0019          41.1%
5x5      X       0.0032        0.0020          35.9%
13x13     Cross   0.0138        0.0040          71.1%
13x13     X       0.0138        0.0044          67.8%
25x25     Cross   0.0452        0.0071          84.2%
25x25     X       0.0451        0.0079          82.4%
50x50     Cross   0.1655        0.0137          91.7%
50x50     X       0.1649        0.0156          90.6%
100x100    Cross   0.6279        0.0269          95.7%
100x100    X       0.6261        0.0304          95.1%
200x200    Cross   2.4607        0.0531          97.8%
200x200    X       2.4432        0.0601          97.5%
400x400    Cross   9.6817        0.1081          98.9%
400x400    X       9.6828        0.1239          98.7%
800x800    Cross   38.4575        0.2203          99.4%
800x800    X       38.4358        0.2593          99.3%
```

앞선 1D 최적화와 정반대 패턴이다: 1D는 상수 인자만 줄여서 N이 커질수록 개선율이 오히려 줄었지만, 이번 건 점근적 복잡도 자체를 O(N²)→O(N)으로 낮췄기 때문에 N이 커질수록 개선율이 계속 커진다(3×3에서 20~24% → 800×800에서 99%대). X는 대각선 인덱싱(`filter[i][n-1-i]`)이 중앙 행/열 인덱싱보다 미세하게 비싸서 Cross보다 개선율이 살짝 낮지만(예: 800×800에서 Cross 99.4% vs X 99.3%) 같은 O(N) 계열로 수렴한다. 800×800 기준 O(N²)는 64만 회 곱셈-누적을 수행하는 반면 O(2N-1)은 1,599회만 수행하므로, 이 비율(약 400배) 차이가 그대로 실측 시간 차이(38.4ms → 0.22~0.26ms, 약 150~175배)에 근접하게 반영된다(완전히 일치하지 않는 이유는 작은 N에서처럼 함수 호출 등 고정 오버헤드가 절대 시간에 일부 섞여 있기 때문).

### 보너스2 — 패턴 생성기 (`bonus2_generator.py`)

`generate_cross_pattern(n)`은 중심 행/열(`n//2`)을 1.0으로 채워 십자가를, `generate_x_pattern(n)`은 두 대각선(`i==col`, `col==n-1-i`)을 1.0으로 채워 X 모양을 만든다(홀수 N 기준, 미션 예시의 3×3 패턴과 동일 규칙을 N으로 일반화). N=5로 실행한 예:

```text
Cross                  X
0 0 1 0 0              1 0 0 0 1
0 0 1 0 0              0 1 0 1 0
1 1 1 1 1              0 0 1 0 0
0 0 1 0 0              0 1 0 1 0
0 0 1 0 0              1 0 0 0 1
```

생성된 패턴은 `mac_calculator.py`의 `MacCalculator.calculate_2d`/`MacCalculator.judge`를 그대로 import해서 판정까지 재활용한다(`run_generated_judgement`) — 위 Cross 패턴을 자기 자신과 대조하면 Cross 점수 9.0, X 점수 1.0으로 정상적으로 Cross 판정이 나온다. `bonus1_optimize.py`도 이 파일의 `generate_cross_pattern`/`generate_x_pattern`을 import해서 벤치마크용 입력으로 재사용한다.

## 재현성 메모

- 사용자 입력 모드 예시(십자가 필터 A `0 1 0 / 1 1 1 / 0 1 0`, X 필터 B `1 0 1 / 0 1 0 / 1 0 1`, 패턴 `1 0 1 / 0 1 0 / 1 0 1`) 입력 시 `A 점수: 1.0`, `B 점수: 5.0`, `판정: B` 정상 출력 확인.
- JSON 모드 실행 시 케이스별 PASS/FAIL과 마지막 "총/통과/실패" 집계가 항상 일치한다(`failed_cases` 리스트 하나로 개별 출력과 합계를 동시에 계산하기 때문).
- `size_5` 필터를 삭제하거나 패턴 크기를 깨뜨린 손상 데이터로 테스트해도 프로그램이 죽지 않고 해당 케이스만 FAIL로 처리하고 계속 진행하는 것을 확인했다.

## 문서 목록

- [main.py](file:///Users/aaa9460994/Desktop/codyssey-mission/E1/3/main.py): 메인 실행 소스코드 (모드 선택 진입점, 실제 로직은 `mac_calculator.py`/`utils/`/`mode/`로 분리됨)
- [bonus/bonus1_optimize.py](file:///Users/aaa9460994/Desktop/codyssey-mission/E1/3/bonus/bonus1_optimize.py): 보너스1, 1D 메모리 접근 최적화 + O(2N-1) 희소 연산 + 성능 비교
- [bonus/bonus2_generator.py](file:///Users/aaa9460994/Desktop/codyssey-mission/E1/3/bonus/bonus2_generator.py): 보너스2, N×N Cross/X 패턴 생성기
