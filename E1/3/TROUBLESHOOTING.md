# 트러블슈팅: Python `map()` 이터레이터 소진으로 인한 MAC 점수 계산 오류

## 1. 개요
* **발생 일자**: 2026-07-30
* **관련 파일**: `E1/3/main.py`
* **현상**: 필터 B와 패턴 입력 시 MAC 연산 결과에서 B 점수가 지속적으로 `0`으로 나오는 현상

---

## 2. 문제 증상

사용자 입력 모드(`modeNum = 1`)에서 다음과 같이 필터 A, 필터 B, 패턴을 입력하여 MAC 결과를 확인했을 때, B 점수가 `0`으로 출력되고 판정이 `판정 불가`로 처리됨.

### 입출력 예시
```text
필터 A (3줄 입력, 공백 구분)
0 1 0
1 1 1
0 1 0

필터 B (3줄 입력, 공백 구분)
1 0 1
0 1 0
1 0 1

패턴 (3줄 입력, 공백 구분)
1 0 1
0 1 0
1 0 1

#---------------------------------------
# [3] MAC 결과 (판정 불가)
#---------------------------------------
A 점수: 1.0
B 점수: 0
판정: 판정 불가 (|A-B| < 1e-9)
```

---

## 3. 원인 분석 (Root Cause Analysis)

### 3.1 Python `map()`의 동작 방식
Python 3에서 `map()` 함수는 **일회성 이터레이터(Iterator)**를 반환합니다. 이터레이터는 내부 요소를 한 번 순회(Iterate)하고 나면 데이터가 소진(Exhausted)되어 재사용할 수 없습니다.

### 3.2 기존 코드 분석
기존 코드에서는 입력받은 매트릭스를 다음과 같이 `map` 객체 형태로 리스트에 추가하였습니다.

```python
# main.py (기존)
cross_filter_matrix.append(map(float, (input().split(" "))))
x_filter_matrix.append(map(float, (input().split(" "))))
pattern_matrix.append(map(float, (input().split(" "))))
```

### 3.3 문제 발생 흐름
1. `cross_filter_point = calculate_mac(cross_filter_matrix, pattern_matrix)` 호출
   - `calculate_mac` 내부의 `zip(f_row_lst, p_row_lst)` 루프를 실행하면서 `pattern_matrix` 행 내부의 `map` 이터레이터 요소들이 순회됩니다.
   - 첫 번째 연산이 끝나면 `pattern_matrix`의 모든 `map` 이터레이터는 소진되어 빈(empty) 이터레이터 상태가 됩니다.
2. `x_filter_point = calculate_mac(x_filter_matrix, pattern_matrix)` 호출
   - `pattern_matrix` 내부의 이터레이터가 이미 소진되어 `for f_val, p_val in zip(f_row_lst, p_row_lst):` 루프가 단 한 번도 실행되지 않습니다.
   - 그 결과 `filter_sum` 초깃값인 `0`이 그대로 반환됩니다 (`B 점수 = 0`).

---

## 4. 해결 방법 (Resolution)

`map()`의 결과를 `list(...)`로 변환하여 메모리에 리스트로 저장하면 여러 번 재 순회하더라도 데이터가 유지됩니다.

### 코드 수정 (Diff)
```diff
- cross_filter_matrix.append(map(float, (input().split(" "))))
+ cross_filter_matrix.append(list(map(float, input().split())))

- x_filter_matrix.append(map(float, (input().split(" "))))
+ x_filter_matrix.append(list(map(float, input().split())))

- pattern_matrix.append(map(float, (input().split(" "))))
+ pattern_matrix.append(list(map(float, input().split())))
```

---

## 5. 수정 후 검증 (Verification)

수정 후 동일한 입력 데이터에 대해 테스트를 진행한 결과:

```text
#---------------------------------------
# [3] MAC 결과
#---------------------------------------
A 점수: 1.0
B 점수: 5.0
연산 시간(평균/10회): 0.0011 ms
판정: B
```

* **A 점수**: `1.0` (정상)
* **B 점수**: `5.0` (정상 계산 완료)
* **판정 결과**: 점수가 `5.0`에 도달한 **B** 필터로 정상 판정됨.

---

## 6. 교훈 및 주의사항 (Best Practices)

1. **이터레이터(Iterator) 재사용 주의**: Python에서 `map`, `filter`, `zip`, `generator` 등은 일회성이므로 여러 함수나 루프에서 재사용할 필요가 있다면 반드시 `list()`나 `tuple()`로 평가(evaluate)하여 보관해야 합니다.
2. **다중 횟수 연산 모듈 (`timeit` 등)**: `timeit`과 같이 인자를 반복적으로 호출하는 함수를 다룰 때 데이터가 소진되는 구조인지 사전에 확인해야 합니다.
