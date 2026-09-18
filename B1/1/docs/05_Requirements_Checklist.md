# 📋 요구사항 구현 체크리스트 (Requirement Checklist)

본 문서는 과제 요구사항(`README.md`) 항목의 구현 여부, 관련 코드 위치, 검증 상태를 점검하고 추적하기 위한 체크리스트입니다.

---

## 📊 진행 상황 요약

- **총 요구사항 항목**: 25개 주요 요구사항 (하위 세부 항목 포함)
- **달성률**: 100% 완료 ✅
- **구현 방식**: 바닐라 자바스크립트(ES Modules) + Web Components (Custom Elements & Shadow DOM) 기반 반응형 SPA

---

## 1. 레이아웃 & 반응형 웹 디자인

| 번호 | 요구사항 | 구현 내용 및 세부 사항 | 상태 | 관련 파일 |
| :--- | :--- | :--- | :---: | :--- |
| **1** | **반응형 웹 (모바일 퍼스트)** | - 모바일 퍼스트 기준 미디어 쿼리 작성<br>- 브레이크포인트: `768px`(태블릿), `1024px`(데스크탑)<br>- 모바일 환경 햄버거 메뉴 토글 동작 (`classList.toggle('active')`) | ✅ | [`style.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/style.css)<br>[`main.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/main.js) |
| **12** | **최소 폴더 구조 & 스타일 규칙** | - `index.html`, `css/`, `js/`, `images/` 폴더 구조 준수<br>- `:root` 전역 CSS 변수로 테마 컬러/간격/폰트 정의<br>- 다크 모드 속성 셀렉터 `[data-theme="dark"]` 스타일 정의<br>- 네비게이션: Flexbox 레이아웃 (로고 \| 메뉴 \| 액션)<br>- Projects 카드: CSS Grid (`repeat(auto-fit, minmax(320px, 1fr))`) | ✅ | [`index.html`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/index.html)<br>[`style.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/style.css)<br>[`ProjectsSection.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/components/ProjectsSection.css) |
| **14** | **시맨틱 태그 활용** | - `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>` 적재적소 적용<br>- Web Components 내부 템플릿에도 시맨틱 태그 구조 유지 | ✅ | [`index.html`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/index.html)<br>[`HeroSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/HeroSection.js) 등 |
| **18** | **버튼/카드 인터랙션** | - 버튼 및 카드 컴포넌트에 `hover` 가상 클래스와 `transition` 속성 적용<br>- 마우스 오버 시 미세한 Y축 이동(`transform: translateY(-4px)`) 효과 | ✅ | 각 컴포넌트 CSS |
| **19** | **카드 그림자(box-shadow)** | - 프로젝트 및 기술 스택 카드에 일관된 `box-shadow` 적용<br>- Hover 시 그림자 깊이감 전환 애니메이션 | ✅ | [`ProjectsSection.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/components/ProjectsSection.css)<br>[`SkillsSection.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/components/SkillsSection.css) |
| **25** | **인라인 스타일 금지** | - 모든 스타일을 외부 CSS 파일로 분리<br>- HTML 태그 내 `style="..."` 사용 배제 | ✅ | 전체 마크업 및 컴포넌트 |

---

## 2. 필수 섹션 및 UI 컴포넌트

| 번호 | 요구사항 | 구현 내용 및 세부 사항 | 상태 | 관련 파일 |
| :--- | :--- | :--- | :---: | :--- |
| **2-1** | **Hero 섹션** | - 타이틀, 자기소개 및 CTA 버튼 (Projects 섹션 바로가기)<br>- **타자기 효과(Typewriter Effect)**: 문장별 한 글자씩 타이핑 및 삭제 반복 연출<br>- 컴포넌트 언마운트 시 `clearTimeout` 타이머 정리 | ✅ | [`HeroSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/HeroSection.js)<br>[`HeroSection.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/components/HeroSection.css) |
| **2-2** | **About 섹션** | - 자기소개 텍스트, 프로필 이미지 및 핵심 가치관/특징 카드 렌더링<br>- 이미지 `alt` 속성 및 에러 대비 플레이스홀더 처리 | ✅ | [`AboutSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/AboutSection.js)<br>[`AboutSection.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/components/AboutSection.css) |
| **2-3** | **Skills 섹션** | - 프론트엔드, 백엔드/인프라, 툴/협업 도구 기술 스택 카테고리화<br>- 태그 및 칩 형태의 직관적인 디자인 | ✅ | [`SkillsSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/SkillsSection.js)<br>[`SkillsSection.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/components/SkillsSection.css) |
| **2-4** | **Projects 섹션** | - GitHub API 연동 카드 목록 동적 렌더링<br>- 언어별 필터링 기능 및 카드 그리드 배치 | ✅ | [`ProjectsSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/ProjectsSection.js)<br>[`ProjectsSection.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/components/ProjectsSection.css) |
| **2-5** | **Contact 섹션 (문의 폼)** | - 이름, 이메일, 메시지 입력 폼 구성<br>- `for`-`id` 매핑 기반 접근성 준수 `<label>` 태그 적용 | ✅ | [`ContactSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/ContactSection.js)<br>[`ContactSection.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/components/ContactSection.css) |
| **2-6** | **Footer 섹션** | - 저작권(Copyright) 문구 및 소셜 미디어/GitHub 링크 연결 | ✅ | [`index.html`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/index.html)<br>[`style.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/style.css) |
| **16** | **이미지 alt 속성** | - 프로필 이미지 및 UI 내 모든 `<img>` 태그에 스크린 리더용 명확한 `alt` 속성 기재 | ✅ | [`AboutSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/AboutSection.js) 등 |

---

## 3. 내비게이션 & 스크롤 인터랙션

| 번호 | 요구사항 | 구현 내용 및 세부 사항 | 상태 | 관련 파일 |
| :--- | :--- | :--- | :---: | :--- |
| **4** | **햄버거 메뉴** | - 모바일 해상도에서 햄버거 토글 버튼 동작<br>- 메뉴 링크 클릭 시 모바일 메뉴 패널 자동 닫힘 처리 | ✅ | [`main.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/main.js)<br>[`style.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/style.css) |
| **5** | **부드러운 스크롤 & 활성 메뉴** | - 네비게이션 앵커 링크 클릭 시 부드러운 스크롤 이동 (`html { scroll-behavior: smooth; }`)<br>- `IntersectionObserver` (임계값 `threshold: 0.3`)로 뷰포트 감지 후 현재 섹션 메뉴 활성화 (Scrollspy) | ✅ | [`main.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/main.js)<br>[`style.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/style.css) |
| **6** | **스크롤 등장 애니메이션** | - `IntersectionObserver`로 섹션 등장 감지 후 `.active` 클래스 부여<br>- 페이드인 및 Y축 슬라이드 애니메이션 효과 | ✅ | [`main.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/main.js)<br>[`style.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/style.css) |
| **15** | **네비게이션 스크롤 스타일 전환** | - 스크롤 60px 초과 시 헤더에 `.scrolled` 클래스 토글<br>- 배경색 반투명 블러(글래스모피즘) 및 하단 보더 생성 | ✅ | [`main.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/main.js)<br>[`style.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/style.css) |
| **20** | **스크롤 탑 버튼** | - 스크롤 300px 초과 시 우하단 플로팅 버튼 표시<br>- 클릭 시 부드럽게 최상단으로 스크롤 이동 (`window.scrollTo({ top: 0, behavior: 'smooth' })`) | ✅ | [`main.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/main.js)<br>[`style.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/style.css) |

---

## 4. 테마 시스템 (다크 모드)

| 번호 | 요구사항 | 구현 내용 및 세부 사항 | 상태 | 관련 파일 |
| :--- | :--- | :--- | :---: | :--- |
| **3** | **다크 모드 시스템 감지** | - `window.matchMedia('(prefers-color-scheme: dark)')`를 통한 OS 설정 감지<br>- OS 테마 변경 시 이벤트 리스너 실시간 반영 | ✅ | [`main.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/main.js) |
| **10** | **로컬스토리지 영속성** | - 사용자 선택 테마(`dark` / `light`)를 `localStorage`에 저장 및 불러오기<br>- 페이지 새로고침 시에도 이전 테마 유지 | ✅ | [`main.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/main.js) |

---

## 5. Contact 폼 및 유효성 검사

| 번호 | 요구사항 | 구현 내용 및 세부 사항 | 상태 | 관련 파일 |
| :--- | :--- | :--- | :---: | :--- |
| **7, 17** | **Form 유효성 검사** | - `event.preventDefault()`로 폼 기본 제출 동작 차단<br>- 필수 입력값 검증 (이름, 이메일, 내용 빈 값 방지)<br>- 이메일 정규표현식(`/^[^\s@]+@[^\s@]+\.[^\s@]+$/`) 포맷 검증<br>- 입력 필드 하단에 실시간 인라인 에러 메시지 노출 (`aria-live="polite"`)<br>- input 이벤트 발생 시 기존 에러 메시지 자동 초기화 | ✅ | [`ContactSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/ContactSection.js) |
| **2-5** | **제출 피드백 & 전송 처리** | - 제출 성공 시 카드 형태의 축하 성공 메시지 UI 표시 및 재작성 버튼 제공<br>- 이메일 서비스(Formspree, EmailJS 등) 연동 가능한 비동기 핸들러 구조화 | ✅ | [`ContactSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/ContactSection.js) |
| **17** | **Label 연결 접근성** | - `<label for="...">`와 `<input id="...">`, `<textarea id="...">` 1:1 완벽 매칭 | ✅ | [`ContactSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/ContactSection.js) |

---

## 6. 비동기 통신 (GitHub REST API 연동)

| 번호 | 요구사항 | 구현 내용 및 세부 사항 | 상태 | 관련 파일 |
| :--- | :--- | :--- | :---: | :--- |
| **8** | **GitHub API 동적 연동** | - `fetch` 및 `async/await` 구문을 활용하여 GitHub 저장소 목록 호출<br>- Fork 저장소 제외 필터링 (`!repo.fork`)<br>- `try / catch`를 통한 통신 예외 처리<br>- 403 Rate Limit (시간당 60회 초과) 대응 UI 분기 처리<br>- 5분간 유효한 `sessionStorage` 캐싱 적용으로 API 호출 낭비 방지 | ✅ | [`ProjectsSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/ProjectsSection.js) |
| **9** | **UI 상태 표현 (Loading / Error / Empty / Success)** | - **로딩 상태**: 스켈레톤 쉬머(Skeleton Shimmer) 카드 애니메이션 표시<br>- **성공 상태**: 저장소 이름, 설명, 스타 수, 언어 배지, 링크 버튼 렌더링<br>- **에러 상태**: "프로젝트를 불러올 수 없습니다" 안내 문구 및 [다시 시도] 버튼 제공<br>- **빈 상태**: "표시할 프로젝트가 없습니다" 안내 문구 노출 | ✅ | [`ProjectsSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/ProjectsSection.js)<br>[`ProjectsSection.css`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/css/components/ProjectsSection.css) |

---

## 7. 모던 자바스크립트 문법 및 코딩 컨벤션

| 번호 | 요구사항 | 구현 내용 및 세부 사항 | 상태 | 관련 파일 |
| :--- | :--- | :--- | :---: | :--- |
| **12** | **ES 모듈 & DOM 조작** | - `script type="module"` (모듈 지연 로딩 특성 포함) 적용<br>- `var` 키워드 완전 배제 (`const`, `let`만 사용)<br>- 인라인 이벤트 리스너(`onclick`) 대신 `addEventListener` 사용<br>- `querySelector`, `querySelectorAll` 표준 DOM 선택자 사용<br>- `classList.add`, `remove`, `toggle`로 안전한 클래스 제어<br>- `click`, `submit`, `scroll`, `input` 등 주요 이벤트 리스너 활용 | ✅ | [`main.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/main.js)<br>모든 JS 컴포넌트 |
| **21** | **화살표 함수 (Arrow Function)** | - 콜백 및 메서드 내부 익명 함수에 화살표 함수 구문 적용 | ✅ | 전체 JS 코드 |
| **22** | **템플릿 리터럴 (Template Literals)** | - 백틱(`` ` ``)을 이용한 동적 HTML 마크업 렌더링 | ✅ | 전체 Web Components |
| **23** | **구조분해 할당 (Destructuring)** | - 객체 및 배열 구조분해 할당 활용 (`const { name, email, message } = this.state.formData;` 등) | ✅ | [`ContactSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/ContactSection.js) 등 |
| **24** | **배열 고차 함수** | - `.map()`: GitHub 저장소 배열을 HTML 카드 마크업 문자열로 변환<br>- `.filter()`: 언어별(All, JavaScript, HTML 등) 프로젝트 필터링 버튼 동작<br>- `.forEach()`: 이벤트 바인딩 및 DOM 노드 순회 처리 | ✅ | [`ProjectsSection.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/components/ProjectsSection.js)<br>[`main.js`](file:///Users/shin-yoonsik/Desktop/codyssey/B1/1/js/main.js) |

---

## 8. 배포 및 개발 환경

| 번호 | 요구사항 | 구현 내용 및 세부 사항 | 상태 | 비고 |
| :--- | :--- | :--- | :---: | :--- |
| **11** | **GitHub Pages 배포** | - 정적 파일 호스팅 배포 지원 구조<br>- 절대 경로 대신 상대 경로(`.` 기반) 리소스 참조 설정 | ✅ | 배포 브랜치 설정 필요 |
| **13** | **Live Server 로컬 환경** | - 로컬 개발 서버(Live Server 등)에서 정상 구동 지원 | ✅ | 브라우저 테스트 완료 |
