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

---

## 2. 다크 모드 영속성 전략 (`localStorage` + `matchMedia`)

사용자 경험(UX)을 극대화하기 위해 3단계 우선순위로 테마를 결정합니다.

1. **1순위 (사용자 선택)**: `localStorage`에 저장된 이전 선택(`dark` 또는 `light`)
2. **2순위 (시스템 환경)**: OS 설정(`window.matchMedia("(prefers-color-scheme: dark)").matches`)
3. **3순위 (기본값)**: `light`

```javascript
// 시스템 설정 실시간 감지 리스너
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", (e) => {
    // 사용자가 수동으로 버튼을 누른 적이 없을 때만 OS 설정에 맞춰 자동 변경
    if (!localStorage.getItem("portfolio_theme")) {
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
sessionStorage.setItem(CACHE_TIME_KEY, String(Date.now()));
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
