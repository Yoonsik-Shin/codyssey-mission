# Web Components 아키텍처 및 BaseComponent 설계

브라우저 표준 기술인 **Web Components**의 핵심 원리와, 리액트처럼 상태 기반 렌더링 및 라이프사이클을 지원하도록 구축한 **`BaseComponent` 추상 클래스 설계**를 정리한 문서입니다.

---

## 1. Web Components의 3대 핵심 표준

| 기술                          | 역할 및 설명                                                             |
| :---------------------------- | :----------------------------------------------------------------------- |
| **Custom Elements**           | HTML 표준에 없는 나만의 태그(예: `<hero-section>`)를 자바스크립트로 정의 |
| **Shadow DOM**                | 컴포넌트 내부의 DOM 트리와 스타일(CSS)을 외부와 완벽히 격리(캡슐화)      |
| **HTML Templates & `<slot>`** | 렌더링 시점에 원하는 위치에 콘텐츠를 투영(Slotting)하여 자식 요소를 주입 |

---

## 2. 웹 컴포넌트 필수 규칙

### ① HTMLElement 상속

모든 커스텀 엘리먼트는 브라우저 내장 클래스인 `HTMLElement`를 반드시 상속(`extends`)받아야 브라우저의 DOM 생명주기 메서드를 사용할 수 있습니다.

### ② Kebab-case 네이밍 규칙 (대시 `-` 필수)

- **HTML은 대소문자를 구분하지 않습니다**: `<HeroSection>`이라고 작성해도 브라우저는 소문자 `<herosection>`으로 파싱합니다.
- **미래의 공식 HTML 태그와의 충돌 방지**: W3C 웹 표준 기구는 공식 HTML 태그에 절대 대시(`-`)를 사용하지 않기로 약속했습니다. 따라서 커스텀 태그는 반드시 대시를 1개 이상 포함해야 합니다.
  - ❌ `customElements.define("herosection", HeroSection)` (에러)
  - ⭕ `customElements.define("hero-section", HeroSection)` (정상)

---

## 3. Shadow DOM과 스타일 캡슐화 (시각적 아키텍처)

Shadow DOM은 메인 웹페이지(Light DOM)와 컴포넌트 내부 사이에 **"보이지 않는 차단벽(Shadow Boundary)"**을 세워 완벽한 캡슐화(Encapsulation)를 보장합니다.

### 1) Light DOM vs Shadow DOM 구조 시각화

```mermaid
graph TD
    subgraph LightDOM ["메인 웹페이지 (Light DOM)"]
        Document["document (최상위 트리)"]
        Header["header#main-header"]
        GlobalCSS["전역 CSS (style.css)"]
        Host["<project-section> (Shadow Host: 문지기 태그)"]
        
        Document --> Header
        Document --> Host
        GlobalCSS -.->|"일반 선택자 차단 ❌<br/>(.project-card, button 등)"| Wall
    end

    subgraph Boundary ["격리 경계선 (Shadow Boundary)"]
        Wall["🧱 #shadow-root (mode: open)"]
    end

    subgraph ShadowTree ["컴포넌트 독립 트리 (Shadow DOM)"]
        CompCSS["컴포넌트 전용 CSS<br/>(ProjectsSection.css)"]
        Container[".projects-container"]
        Cards[".project-card"]
        Button["button.filter-btn"]

        Wall --> CompCSS
        Wall --> Container
        Container --> Cards
        Container --> Button
    end

    Host --> Wall
    GlobalCSS ==>|"💡 유일한 관통 허용: CSS 변수<br/>var(--primary-color), var(--card-bg)"| ShadowTree
```

### 2) 왜 `this.attachShadow({ mode: "open" })`을 쓰는가?

| 비교 관점 | 일반 DOM (Light DOM) | 섀도우 돔 (Shadow DOM) |
| :--- | :--- | :--- |
| **CSS 스타일 범위** | **전역(Global)**: 클래스명이 겹치면 페이지 전체가 오염됨 | **지역(Scoped)**: 컴포넌트 내부 CSS는 절대 밖으로 새지 않음 |
| **외부 스타일 영향** | 부모/전역 스타일의 영향을 무조건 받음 | **원천 차단**: 전역 태그 선택자가 내부로 침투하지 못함 |
| **DOM 탐색 (`querySelector`)** | `document.querySelector('button')`으로 모두 잡힘 | 외부 `document` 탐색에서 제외되어 완벽히 은닉됨 |
| **예외 관통 규칙** | 해당 없음 | **CSS 변수(`var(--...)`)만 유일하게 경계를 뚫고 상속**됨 |

---

## 4. `BaseComponent` 추상 클래스 설계 원리

반복되는 웹 컴포넌트 보일러플레이트를 제거하고 일관된 컨벤션을 위해 설계된 부모 클래스입니다.

### 핵심 기능 매커니즘

1. **상태 관리 (`state` & `setState`)**:
   - `this.state` 변경 시 자동으로 `_renderWithStyle()`이 호출되어 화면을 다시 그립니다.
2. **1:1 CSS 파일 매핑 컨벤션**:
   - `BaseComponent.resolveCss("ComponentName.css")`를 통해 자식 클래스와 동일한 이름의 CSS 파일이 자동으로 링크됩니다.
3. **비동기 `mounted()` 라이프사이클 자동 감지**:
   - 자식 컴포넌트의 `mounted()`가 `Promise`(async)를 반환하면, 부모 클래스가 자동으로 `isLoading: true` 상태로 전환하여 **스켈레톤/스피너**를 띄우고, 완료 시 해제합니다.
4. **에러 바운더리(Error Boundary)**:
   - 비동기 통신 실패나 렌더링 에러 발생 시 컴포넌트가 깨지지 않고 공통 에러 박스(`renderError`)를 출력합니다.

```javascript
// BaseComponent.js 핵심 구조
export class BaseComponent extends HTMLElement {
  #isMounted = false;
  #stylesInjected = false;

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.state = { isLoading: false, error: null };
  }

  connectedCallback() {
    this.#renderWithStyle();
    if (!this.#isMounted) {
      this.#isMounted = true;
      this.#handleMounted();
    }
  }

  async #handleMounted() {
    try {
      const result = this.mounted();
      if (result instanceof Promise) {
        this.setState({ isLoading: true, error: null });
        await result;
        this.setState({ isLoading: false });
      }
    } catch (err) {
      this.setState({ isLoading: false, error: err });
    }
  }

  // ⭐️ 성능 최적화: 스타일시트 최초 1회만 주입하여 FOUC 및 CSSOM 재파싱 방지
  #ensureStyles() {
    if (this.#stylesInjected) return;
    this.#stylesInjected = true;

    const baseLink = document.createElement("link");
    baseLink.rel = "stylesheet";
    baseLink.href = BaseComponent.resolveCss("BaseComponent.css");
    this.shadowRoot.appendChild(baseLink);

    if (this.cssPath) {
      const childLink = document.createElement("link");
      childLink.rel = "stylesheet";
      childLink.href = this.cssPath;
      this.shadowRoot.appendChild(childLink);
    }

    const container = document.createElement("div");
    container.className = "component-container";
    this.shadowRoot.appendChild(container);
  }

  #renderWithStyle() {
    this.#ensureStyles();

    let html = "";
    if (this.state.error) html = this.renderError(this.state.error);
    else if (this.state.isLoading) html = this.renderLoading();
    else html = this.render();

    const container = this.shadowRoot.querySelector(".component-container");
    if (container) {
      container.innerHTML = html;
    }

    if (!this.state.isLoading && !this.state.error) {
      this.setEvents();
    }
  }
}
```

---

## 5. ⭐️ [A to Z] 브라우저 웹 컴포넌트 완벽 렌더링 라이프사이클 흐름도

브라우저가 HTML을 처음 읽는 순간부터 최종 데이터가 화면에 출력될 때까지 **언제, 어떤 것이, 어떻게 렌더링되는지**의 전체 흐름입니다.

### 1) 한눈에 보는 통합 렌더링 타임라인 흐름도

```mermaid
sequenceDiagram
    autonumber
    actor User as 사용자
    participant Browser as 브라우저 엔진 (HTML/CSS 파서)
    participant Module as main.js (진입점)
    participant Comp as ProjectsSection (컴포넌트 인스턴스)
    participant Shadow as Shadow DOM (격리 렌더 트리)
    participant Net as GitHub API (백그라운드 통신)

    Note over User,Browser: [단계 1: 브라우저 초기 로딩]
    User->>Browser: index.html 요청 및 파싱 시작
    Browser->>Browser: <header>, <main>, <project-section> 태그 파싱
    Note over Browser: <project-section>은 아직 미등록 상태<br/>(HTMLUnknownElement로 일단 DOM에 자리만 잡아둠)
    
    Note over Browser,Module: [단계 2: 자바스크립트 모듈 실행 & 업그레이드]
    Browser->>Module: defer 스크립트 실행 (main.js)
    Module->>Comp: customElements.define('project-section', ProjectsSection)
    Browser->>Comp: ⭐️ 커스텀 엘리먼트 업그레이드!<br/>new ProjectsSection() [constructor 실행]
    Note over Comp: this.state = { isLoading: true, repos: [] }<br/>attachShadow({ mode: 'open' })

    Note over Comp,Shadow: [단계 3: 첫 번째 렌더링 (First Paint: 스켈레톤)]
    Comp->>Comp: connectedCallback() 진입
    Comp->>Shadow: #renderWithStyle() 호출
    Comp->>Shadow: 1) <style> 인라인 크리티컬 CSS 주입 (쉬머 애니메이션 즉각 가동)
    Comp->>Shadow: 2) 외부 CSS (<link>) 비동기 다운로드 요청 트리거
    Comp->>Shadow: 3) isLoading: true 분기 -> ProjectsLoadingView.render() 주입
    Note over Shadow,Browser: ⚡️ 0ms 즉시 실행: 사용자는 빈 화면 대신 스켈레톤 카드를 봄!
    
    Note over Comp,Net: [단계 4: 비동기 데이터 요청 (Non-blocking)]
    Comp->>Comp: #handleMounted() -> mounted() 호출
    Comp->>Net: #fetchRepositories() (fetch() 백그라운드 호출)
    Note over Comp,Net: 💡 API 응답을 기다리지 않고 브라우저는 화면을 계속 그림!

    Note over Browser,Shadow: [단계 5: CSS 다운로드 완료 & 페이드인]
    Browser-->>Shadow: ProjectsSection.css 다운로드 완료 (link.onload)
    Shadow->>Shadow: .component-container에 'styles-ready' 클래스 추가
    Note over Shadow,User: 🎨 FOUC(날 것의 글자 깜빡임) 없이 부드러운 Fade-in 전환

    Note over Net,Comp: [단계 6: 데이터 도착 & 최종 재렌더링]
    Net-->>Comp: GitHub API 200 OK 응답 (JSON 데이터 도착)
    Comp->>Comp: this.setState({ repos: data, isLoading: false })
    Comp->>Shadow: #renderWithStyle() 재호출
    Comp->>Shadow: isLoading: false 분기 -> ProjectsGridView.render() 템플릿 주입
    Comp->>Shadow: setEvents() 실행 (언어 필터 버튼 이벤트 리스너 바인딩)
    Note over Shadow,User: 🎉 스켈레톤이 실제 GitHub 프로젝트 카드들로 깔끔하게 교체 완료!
```

---

### 2) 단계별 핵심 동작 요약표

| 단계 | 실행 시점 | 렌더링 주체 | 실제 화면에 그려지는 내용 (화면 상태) | 핵심 설계 의도 & 기술 포인트 |
| :--- | :--- | :--- | :--- | :--- |
| **1. HTML 파싱** | `0ms` | 브라우저 엔진 | 헤더, 푸터 등 일반 HTML 요소만 노출 | `<project-section>`은 미등록 상태로 대기 |
| **2. 인스턴스 생성** | `~10ms` | `constructor()` | 화면 변화 없음 (메모리 상태) | `attachShadow()`, 초기 상태 `isLoading: true` 확정 |
| **3. 1차 렌더링** | `~15ms` | `connectedCallback()` | **✨ 스켈레톤 쉬머 애니메이션 노출** | 외부 CSS 지연 시에도 깨지지 않도록 인라인 크리티컬 스타일 즉시 가동 |
| **4. 비동기 통신** | `~20ms` | `mounted()` | **스켈레톤 유지 (화면 멈춤 없음)** | **비차단(Non-blocking)**: 메인 스레드를 멈추지 않고 백그라운드에서 `fetch()` |
| **5. 스타일 동기화** | `~50ms` | `<link onload>` | 스켈레톤 레이아웃이 정확한 그리드로 정렬 | CSS가 늦게 로드되더라도 글자만 튀는 **FOUC 완벽 방지 (`styles-ready`)** |
| **6. 2차 재렌더링** | `~300ms` | `setState()` | **🚀 실제 GitHub 프로젝트 카드 완성 화면** | `isLoading: false`로 전환되면서 템플릿 교체 및 이벤트 리스너 바인딩 |

---

### 3) 만약 API에서 에러가 발생한다면? (에러 라이프사이클)

```mermaid
flowchart LR
    A["mounted() fetch() 실패"] --> B["1초 후 1차 재시도"]
    B --> C["2초 후 2차 재시도 (지수 백오프)"]
    C --> D["최종 실패: catch(err)"]
    D --> E["setState({ isLoading: false, error: err })"]
    E --> F["#renderWithStyle() 재호출"]
    F --> G["ProjectsErrorView.render()<br/>(⚠️ 에러 메시지 + [다시 시도] 버튼 렌더링)"]
    G --> H["사용자가 [다시 시도] 클릭"]
    H --> I["sessionStorage.clear() 후 다시 3단계(스켈레톤)로 진입"]
```

---

## 6. 컴포넌트 분리의 적정선 (과도한 분리 방지)

| 분류                       | 대상                                                                                                | 분리 판단 기준                                                                                                                 |
| :------------------------- | :-------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| **분리 권장 (컴포넌트화)** | `ProjectsSection`, `ContactSection`                                                                 | **독립적인 상태(State), 비동기 API 통신, 사용자 입력 유효성 검사** 등 고유한 비즈니스 로직이 있을 때                           |
| **통합 권장 (단순화)**     | `GreetingsText`, `CtaButton` ➔ `HeroSection`                                                        | 특정 부모 안에서만 단 1회 쓰이거나 단순 래퍼일 때는 컴포넌트를 분리하지 않고 **부모 하나로 응집**시키는 것이 유지보수에 유리함 |
| **중복 래퍼 제거**         | `<section id="skills"><skills-section></section>` ➔ `<skills-section id="skills"></skills-section>` | 커스텀 엘리먼트 자체도 일반 DOM 노드이므로 직접 `id`와 `class`를 가질 수 있음                                                  |
