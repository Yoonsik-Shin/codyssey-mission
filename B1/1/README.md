## 요구사항

1. 반응형 -> 모바일 퍼스트
   - 브레이크 포인트 : 768px (태블릿), 1024px (데스크탑)
   - 모바일에서는 햄버거 메뉴로 네비게이션을 보여줌 (`classList.toggle('active')` 활용)
2. 특정 섹션을 포함되어야함 (Hero, About, Skills, Projects, Contact, Footer)
   - Hero (인사말, CTA 버튼)
     - 타자기처럼 한 글자씩 나타나는 효과를 구현
   - About (자기소개, 프로필 이미지)
   - Skills (기술 스택 목록)
   - Projects (GitHub API 연동 카드)
   - Contact (문의 폼)
     - 이름, 이메일, 메시지
     - 필수값 검증 (빈 필드 금지)
     - 이메일 형식 검증
     - 에러메시지 입력 필드 근처에 표시
     - 제출 시 `event.preventDefault()`로 기본 제출 동작을 막아야함
     - 제출 성공 시 success 메세지 출력
   - Footer (저작권, 소셜 링크)
3. 다크모드 토글
   - 시스템 다크 모드 감지
   - prefers-color-scheme 미디어 쿼리로 시스템 설정을 감지
4. 햄버거 메뉴
5. 부드러운 스크롤
   - 네비게이션 메뉴 클릭 시 해당 섹션으로 부드럽게 이동한다.
   - Intersection Observer 임계값(threshold)은 0.2 이상을 권장
6. 스크롤 애니메이션
7. Form 유효성 검사
8. Github API로 저장소 목록을 가져와 Projects 섹션에 동적으로 렌더링
   - `fetch` 사용
   - `async/await` 활용
   - `https://api.github.com/users/{본인아이디}/repos`
   - try/catch로 에러를 처리
   - 레이트 리밋 발생 시(403 응답) 에러 상태 UI가 표시되도록 처리
9. 로딩/에러/빈 상태 표현
   - 로딩 상태: 데이터 요청 중 스피너 또는 "로딩 중..." 텍스트
   - 성공 상태: 카드 리스트 렌더링
   - 에러 상태: "프로젝트를 불러올 수 없습니다" 메시지 + 재시도 버튼
   - 빈 상태: "표시할 프로젝트가 없습니다" 메시지
10. 다크모드 설정이 로컬 스토리지에 저장되어 새로고침 후에도 유지되어야함
11. Github Pages로 배포하여 외부접속가능 URL을 생성해야함
12. 최소 폴더구조
    - index.html (메인페이지)
    - css/style.css (스타일시트)
      - :root CSS 변수로 색상, 폰트, 간격 정의
      - 다크모드용 CSS 변수 정의 (`[data-theme="dark]`)
      - 네비게이션 Flexbox 사용 (로그 | 메뉴)
      - Projects 카드 Grid 사용 (`auto-fit`, `minmax`로 반응형)
    - js/ (Javascript 파일)
      - js 파일 `defer` 속성으로 연결 -`var` 사용금지
      - `onclick` 대신 `addEventListener` 사용
      - `querySelector`, `querySelectorAll`사용
      - `textContent`, `innerHTML` 사용
      - `classList.add`, `remove`, `toggle` 로 클래스 조작 ???
      - `click`, `submit`, `scroll`, `input` 이벤트 사용
      - `event.preventDefault()` 사용
    - images/ (이미지 파일)
13. Live Server로 실시간 개발 환경을 구성
14. 시맨틱 태그 사용해야함 (head, nav, main, section, article, footer 등등)
15. 네비게이션
    - 앵커 링크
    - 스크롤 60px 이상에서 네비게이션 배경색이 변경
16. 이미지에 alt 속성 작성
17. 폼
    - label 태그 올바르게 연결 (for-id 매칭)
    - 실제 전송 -> Formspree 또는 EmailJS를 연동하여 실제 이메일을 전송
18. 버튼/카드 `hover + transition`
19. 카드에 `box-shadow` 적용
20. 스크롤 탑 버튼
    - 스크롤 300px 이상에서 버튼 나타나도록
21. 화살표 함수 적절히 사용
22. 템플릿 리터럴로 HTML 동적 생성
23. 구조분해 할당 적절히 사용
24. 배열 메서드 활용
    - `map` : GitHub 데이터를 HTML 카드로 변환
    - `filter` : 특정 조건의 프로젝트만 표시 -> GitHub 프로젝트를 언어별로 필터링하는 버튼
    - `forEach` :배열 순회
25. 인라인 스타일(style="...") 사용 금지

## 설명가능한 목표

- HTML에서 시맨틱 태그를 왜 사용하는지 또한 본인이 어떤 기준으로 구조를 설계했는지 설명할 수 있다.
- CSS에서 Flexbox와 Grid의 차이, 그리고 언제 각각을 선택해야 하는지 설명할 수 있다.
- querySelector로 DOM을 선택하고, addEventListener로 이벤트를 연결하는 흐름을 설명할 수 있다.
- 화살표 함수, 구조분해 할당, 배열 메서드(map/filter)가 왜 필요하고 어떻게 사용하는지 설명할 수 있다.
- fetch와 async/await로 비동기 데이터를 가져오고, 로딩/성공/실패 상태를 UI로 어떻게 표현했는지 설명할 수 있다.
- "하나의 기능"을 만들기 위해 이벤트 → 상태 변경 → DOM 업데이트가 어떻게 연결되는지 설명할 수 있다. (React의 상태-렌더링 흐름의 기초)
