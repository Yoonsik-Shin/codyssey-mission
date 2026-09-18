# JavaScript 및 모던 브라우저 API 활용

바닐라 자바스크립트로 구현된 스크롤 인터랙션, 시스템 감지, 비동기 통신 및 캐싱 전략, 폼 유효성 검증 기술을 정리한 문서입니다.

---

## 1. Intersection Observer API (스크롤 감지 최적화)

기존 `window.addEventListener('scroll')` 방식은 스크롤할 때마다 수백 번씩 함수가 실행되어 메인 스레드 성능을 저하시킵니다. 반면 **Intersection Observer API**는 브라우저가 화면 교차 여부를 비동기적으로 효율적으로 감지합니다.

### 구현 원리

```javascript
const observerOptions = {
  root: null, // 뷰포트 기준
  threshold: 0.25, // 요소의 25% 이상이 화면에 보일 때 트리거
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      // 1. 섹션 페이드인 애니메이션 활성화
      entry.target.classList.add("active");

      // 2. 현재 보이는 섹션의 네비게이션 메뉴에 .active 하이라이트
      const id = entry.target.getAttribute("id");
      updateActiveNav(id);
    }
  });
}, observerOptions);

document.querySelectorAll(".reveal").forEach((el) => observer.observe(el));
```

### ⭐️ 스크롤 이벤트 성능 최적화 (`requestAnimationFrame` & `passive`)

단순 `scroll` 이벤트 리스너는 사용자가 빠르게 스크롤할 때 초당 수백 회 이상 트리거되어 메인 스레드를 차단하고 레이아웃 스래싱(Layout Thrashing)을 유발합니다. 이를 방어하기 위해 `requestAnimationFrame` 쓰로틀링과 `passive` 리스너를 적용했습니다.

```javascript
let ticking = false;

window.addEventListener(
  "scroll",
  () => {
    if (!ticking) {
      window.requestAnimationFrame(() => {
        const scrollY = window.scrollY;
        // 60fps 디스플레이 주사율(약 16ms)에 맞춰 브라우저 렌더링 직전 1회만 계산
        if (header) header.classList.toggle("scrolled", scrollY > 60);
        if (scrollTopBtn) scrollTopBtn.classList.toggle("visible", scrollY > 300);
        ticking = false;
      });
      ticking = true;
    }
  },
  { passive: true }, // 기본 스크롤 동작 지연 방지
);
```

---

## 2. 다크 모드 영속성 전략 (`localStorage` + `matchMedia`)

사용자 경험(UX)을 극대화하기 위해 3단계 우선순위로 테마를 결정합니다.

1. **1순위 (사용자 선택)**: `localStorage`에 저장된 이전 선택(`dark` 또는 `light`)
2. **2순위 (시스템 환경)**: OS 설정(`window.matchMedia("(prefers-color-scheme: dark)").matches`)
3. **3순위 (기본값)**: `light`

### 1) `window.matchMedia()`란?

- **개념**: CSS 미디어 쿼리(Media Query)를 자바스크립트에서 직접 평가하고 실시간 상태 변화를 구독(구독/발행)할 수 있는 브라우저 표준 Web API입니다.
- **`prefers-color-scheme: dark`**: 사용자의 운영체제(macOS, Windows, iOS 등) 시스템 설정이 다크 모드로 켜져 있는지를 감지하는 미디어 쿼리입니다.
- **반환 객체 (`MediaQueryList`)**:
  - `mediaQuery.matches`: 현재 시점에 미디어 쿼리가 일치하는지 여부 (`true` / `false`)
  - `mediaQuery.addEventListener("change", callback)`: OS 설정이 라이트 ↔ 다크로 실시간 변경될 때 즉각 이벤트 트리거

### 2) 구현 코드 및 동작 흐름

```javascript
const THEME_STORAGE_KEY = "portfolio_theme";

// 1. 초기 로드 시: 사용자가 이전에 저장한 테마가 없으면 OS 설정을 읽음
const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
const initialTheme = savedTheme || (systemPrefersDark ? "dark" : "light");

applyTheme(initialTheme);

// 2. 실시간 감지: 웹페이지를 켜둔 상태에서 OS 테마가 바뀔 때 반응
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", (e) => {
    // 💡 중요: 사용자가 웹사이트에서 직접 버튼을 눌러 고른 적이 없을 때만 OS를 따라감
    if (!localStorage.getItem(THEME_STORAGE_KEY)) {
      applyTheme(e.matches ? "dark" : "light");
    }
  });
```

---

## 3. GitHub API 연동과 Rate Limit 방어 (캐싱 전략)

### GitHub API 비인증 호출의 제약

- 인증 토큰 없이 호출하는 공개 API는 **IP당 시간당 60회**로 엄격히 제한됩니다.
- 개발 중 페이지를 몇 번 새로고침하면 금방 `403 Forbidden` 에러가 발생합니다.

### 해결책: `sessionStorage` 5분 캐시 패턴

```javascript
const CACHE_KEY = `github_repos_${username}`;
const CACHE_TIME_KEY = `${CACHE_KEY}_time`;
const CACHE_EXPIRE = 1000 * 60 * 5; // 5분

// 1. 캐시가 유효하면 네트워크 요청 없이 캐시 데이터 사용
const cachedData = sessionStorage.getItem(CACHE_KEY);
const cachedTime = sessionStorage.getItem(CACHE_TIME_KEY);

if (
  cachedData &&
  cachedTime &&
  Date.now() - Number(cachedTime) < CACHE_EXPIRE
) {
  this.setState({ repos: JSON.parse(cachedData) });
  return;
}

// 2. 캐시 만료 시에만 실제 API fetch 수행
const res = await fetch(
  `https://api.github.com/users/${username}/repos?sort=updated&per_page=12`,
);
if (!res.ok) {
  if (res.status === 403) throw new Error("API 요청 횟수를 초과했습니다.");
  throw new Error("저장소를 불러오지 못했습니다.");
}
const data = await res.json();
sessionStorage.setItem(CACHE_KEY, JSON.stringify(data));
```

### 💡 브라우저 콘솔에서 상태 전환(로딩/에러/빈 상태) 검증

컴포넌트의 단방향 상태 렌더링 파이프라인이 정상 동작하는지 브라우저 개발자 도구(F12) 콘솔에서 아래 명령어로 즉시 테스트할 수 있습니다:

```javascript
// 1. 로딩 상태 (스켈레톤 반짝임 UI)
document.querySelector('project-section').setState({ isLoading: true });

// 2. 에러 상태 (경고 아이콘 + '다시 시도' 버튼 UI)
document.querySelector('project-section').setState({ 
  isLoading: false, 
  error: new Error("네트워크 연결이 끊어졌습니다. (테스트 에러)") 
});

// 3. 빈 상태 (Empty State - 표시할 프로젝트 없음)
document.querySelector('project-section').setState({ 
  isLoading: false, 
  error: null, 
  repos: [] 
});

// 4. 원래 상태로 복구
const p = document.querySelector('project-section');
p._isMounted = false;
p.connectedCallback();
```

---

## 4. 타자기 효과(Typewriter)와 메모리 누수 방지

문자열을 한 글자씩 출력하고 삭제하는 애니메이션을 재귀 `setTimeout`으로 구현했습니다.

### ⭐️ 메모리 누수(Memory Leak) 방지

컴포넌트가 화면에서 사라졌는데도 `setTimeout`이 계속 돌면 백그라운드 자원을 낭비하게 됩니다. 따라서 `unmounted()` 라이프사이클에서 타이머를 반드시 해제해야 합니다.

```javascript
mounted() {
  this.type(); // 시작
}

unmounted() {
  if (this.timer) {
    clearTimeout(this.timer); // 화면에서 없어지면 즉시 중단!
  }
}
```

---

## 5. 폼(Form) 유효성 검증과 이벤트 제어

1. **기본 전송 차단**: `event.preventDefault()`로 페이지 새로고침 방지
2. **이메일 정규식 검증**: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
3. **실시간 에러 클리어**: 사용자가 입력을 시작(`input` 이벤트)하면 빨간색 에러 메시지를 즉시 지워줌
4. **접근성 매칭**: `<label for="email">`과 `<input id="email">`을 1:1 연결하여 라벨 클릭 시 해당 인풋에 포커스 이동
5. **⭐️ 성능 최적화 (미세 DOM 업데이트)**: 유효성 검사 에러 시 `this.setState({ errors })`로 폼 전체 `innerHTML`을 파괴하지 않고, `#applyErrorsToDom()`을 통해 에러 텍스트 노드(`textContent`)와 `invalid` 클래스만 직접 업데이트하여 입력 포커스 유지 및 리플로우 최소화

---

## 6. 스크립트 로딩 전략: `defer` 속성과 `type="module"`

HTML 파서는 `<script>` 태그를 만나는 순간 파싱을 일시 중단(Parser Blocking)하고 스크립트를 다운로드 및 실행합니다. 이를 최적화하기 위해 `defer` 속성을 사용합니다.

```html
<!-- HTML 파싱을 차단하지 않고 백그라운드 다운로드 후, DOM 생성이 끝난 직후 실행 -->
<script type="module" defer src="./js/main.js"></script>
```

### 1) 일반 스크립트 vs `async` vs `defer` 비교

| 속성 | 다운로드 시점 | 실행 시점 | 실행 순서 보장 | DOM 조작 안전성 |
| :--- | :--- | :--- | :---: | :---: |
| **일반 `<script>`** | 파싱 중단 후 즉시 다운로드 | 다운로드 완료 즉시 실행 (HTML 파싱 중단) | ❌ (위치 종속) | ⚠️ 위험 (DOM 미완성 상태) |
| **`<script async>`** | HTML 파싱과 병렬 다운로드 | 다운로드 완료 즉시 실행 (HTML 파싱 일시 중단) | ❌ (먼저 다운로드된 순서) | ⚠️ 위험 (순서 불확실) |
| **`<script defer>`** | HTML 파싱과 병렬 다운로드 | **HTML 파싱 완료 직후 (`DOMContentLoaded` 직전)** | ✅ 보장 (마크업 작성 순서) | ✅ **완벽히 안전** |

### 2) `type="module"`과 `defer`의 관계

- ES 모듈(`type="module"`)은 브라우저 표준 사양상 기본적으로 **지연 평가(Deferred execution)** 방식으로 동작합니다. 즉, HTML 파싱을 블로킹하지 않고 백그라운드에서 다운로드된 뒤 DOM 트리가 완성된 후 실행됩니다.
- 본 프로젝트에서는 모듈 자체의 지연 로딩 특성을 활용함과 동시에, **과제 요구사항 및 정적 검사기 기준을 명확히 충족하기 위해 `<script type="module" defer src="./js/main.js"></script>` 형태로 `defer` 속성을 명시**하였습니다.
- 이를 통해 DOM 요소를 조회(`querySelector`)하는 초기화 코드(`initTheme`, `initNavigation` 등)가 항상 완성된 DOM 트리 위에서 에러 없이 안정적으로 동작하도록 보장합니다.
