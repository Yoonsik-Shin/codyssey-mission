# CSS 아키텍처, 다크 모드 및 반응형 설계

모바일 퍼스트(Mobile First) 반응형 웹 설계, CSS 변수를 활용한 다크 모드 시스템, 그리고 Flexbox와 Grid의 선택 기준을 정리한 문서입니다.

---

## 1. CSS Custom Properties(변수)와 다크 모드

### CSS 변수 선언과 사용
- 접두사 `--`를 붙여 변수를 선언하고, `var(--변수명, 대체값)` 함수로 사용합니다.

```css
:root {
  --bg-primary: #f8fafc;
  --text-primary: #0f172a;
  --primary-color: #2563eb;
}

[data-theme="dark"] {
  --bg-primary: #0b0f19;
  --text-primary: #f8fafc;
  --primary-color: #3b82f6;
}
```

### ⭐️ 핵심: Shadow DOM 경계를 뚫는 CSS 변수 상속
- Shadow DOM의 스타일 캡슐화 때문에 외부 CSS 규칙(`p { color: red; }`)은 컴포넌트 내부로 들어가지 못합니다.
- **그러나 CSS 변수(Custom Properties)는 예외적으로 Shadow DOM의 경계를 관통하여 안쪽까지 그대로 상속됩니다!**
- 따라서 컴포넌트 내부에서 `background-color: var(--card-bg);`처럼 작성하면, 부모(Light DOM)에서 다크모드 속성(`data-theme="dark"`)을 바꿨을 때 모든 웹 컴포넌트의 색상이 자동으로 전환됩니다.

---

## 2. Flexbox vs CSS Grid 비교 및 선택 기준

| 구분 | Flexbox (1차원) | CSS Grid (2차원) |
| :--- | :--- | :--- |
| **축(Axis)** | 가로(Row) 또는 세로(Column) **한 방향** | 가로 행(Row)과 세로 열(Column) **양방향 동시 제어** |
| **주요 용도** | 네비게이션 바(좌우 정렬), 버튼 그룹, 아이콘+텍스트 정렬 | 프로젝트 카드 리스트, 기술 스택 그리드 등 행/열이 교차하는 레이아웃 |
| **프로젝트 적용 예시** | `.navbar` (로고 좌측, 메뉴 중앙, 토글 우측) | `.projects-grid` (`repeat(auto-fit, minmax(300px, 1fr))`) |

### 반응형 카드의 핵심: `auto-fit`과 `minmax`
미디어 쿼리(`@media`)를 덕지덕지 작성하지 않고도 화면 너비에 맞춰 카드가 1개, 2개, 3개로 유연하게 늘어나고 줄어들게 만드는 최신 Grid 패턴입니다.

```css
.projects-grid {
  display: grid;
  /* 화면 너비가 허용하는 한 300px 이상의 카드를 가능한 많이 한 줄에 채움 */
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}
```

---

## 3. 모바일 퍼스트(Mobile First) 전략

- **원칙**: 모바일 화면(작은 화면)을 기본 스타일로 먼저 작성하고, 화면이 넓어질수록 `@media (min-width: ...)`로 기능을 확장합니다.
- **장점**: 모바일 환경에서 불필요한 데스크탑 스타일을 덮어쓰지 않아 렌더링 성능이 우수하고 코드가 간결해집니다.

```css
/* 1. 기본 스타일 (모바일): 세로 1열 배치 */
.about-content {
  display: flex;
  flex-direction: column;
}

/* 2. 태블릿 & 데스크탑 (768px 이상): 가로 2열 배치 */
@media (min-width: 768px) {
  .about-content {
    flex-direction: row;
  }
}
```

---

## 4. 모던 인터랙션 스타일 기법

1. **글래스모피즘 (Glassmorphism)**
   - `backdrop-filter: blur(10px);`를 사용해 스크롤 시 헤더 뒷배경이 부드럽게 비치도록 구현
2. **쉬머 스켈레톤 애니메이션 (`@keyframes base-shimmer`)**
   - 그라디언트 배경(`background-size: 200% 100%`)의 위치를 0%에서 100%로 움직여 빛이 흐르는 로딩 효과 구현
3. **카드 호버 인터랙션**
   - `transform: translateY(-4px);`와 `box-shadow`를 함께 사용하여 마우스 오버 시 카드가 위로 입체적으로 떠오르는 효과 구현
