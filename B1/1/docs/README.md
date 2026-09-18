# 📚 프로젝트 기술 문서 (Documentation)

포트폴리오 웹사이트를 바닥부터 바닐라 자바스크립트와 웹 표준 기술로 구축하며 적용한 핵심 아키텍처 및 기술 개념을 정리한 문서 모음입니다.

---

## 📑 목차 (Table of Contents)

### [1. Web Components 아키텍처 및 BaseComponent 설계](./01_Web_Components.md)

- Custom Elements, Shadow DOM, `<slot>`의 개념과 규칙
- Kebab-case 태그 네이밍 필수 규칙의 이유 (대소문자 무시, 미래 태그 충돌 방지)
- `BaseComponent` 추상 클래스 설계 (상태 관리, 1:1 CSS 매핑, 비동기 마운트, 에러 바운더리)
- 컴포넌트 과도한 분리 방지 및 응집도 기준

### [2. Semantic HTML과 웹 접근성](./02_Semantic_HTML.md)

- 주요 시맨틱 태그(`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`)의 역할
- 시맨틱 마크업을 사용해야 하는 이유 (SEO, 스크린 리더 접근성, 유지보수성)
- 커스텀 엘리먼트와 시맨틱 태그의 조화 (불필요한 이중 래퍼 안티패턴 해결)

### [3. CSS 아키텍처, 다크 모드 및 반응형 설계](./03_CSS_and_Theming.md)

- CSS Custom Properties(변수)를 활용한 다크 모드 시스템
- **Shadow DOM 경계를 관통하여 상속되는 CSS 변수 메커니즘**
- Flexbox vs CSS Grid 비교 및 선택 기준 (`repeat(auto-fit, minmax(300px, 1fr))`)
- 모바일 퍼스트(Mobile First) 반응형 웹 설계 원칙
- 글래스모피즘, 스켈레톤 쉬머 애니메이션, 카드 호버 인터랙션

### [4. JavaScript 및 모던 브라우저 API 활용](./04_Browser_APIs_and_JS.md)

- `IntersectionObserver`를 활용한 고성능 스크롤 페이드인 및 네비게이션 스크롤 스파이
- `localStorage`와 `prefers-color-scheme`를 결합한 테마 영속성
- GitHub REST API 연동 및 시간당 60회 제한을 방어하는 `sessionStorage` 5분 캐싱 전략
- 타자기 효과(Typewriter Effect)의 재귀 타이머 구현과 `unmounted()` 메모리 누수 방지
- Contact 폼 유효성 검사, 정규식 이메일 검증, `event.preventDefault()`

### [5. 요구사항 구현 체크리스트](./05_Requirements_Checklist.md)

- 과제 요구사항 항목별 상세 구현 내용 및 반영 상태 점검표
- 관련 소스 코드 파일 경로 매핑
