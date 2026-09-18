export class BaseComponent extends HTMLElement {
  #isMounted = false;
  #stylesInjected = false;

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.state = {
      isLoading: false,
      error: null,
    };
  }

  // 어떤 속성(attribute)을 감시할지 브라우저에게 알려줌 (자식 클래스에서 오버라이딩)
  static get observedAttributes() {
    return [];
  }

  /** @override */
  connectedCallback() {
    this.#renderWithStyle();

    if (!this.#isMounted) {
      this.#isMounted = true;
      this.#handleMounted();
    }
  }

  /** @override */
  disconnectedCallback() {
    this.unmounted();
  }

  /** 컴포넌트 재마운트 및 데이터 재호출 메서드 (테스트 및 수동 갱신용) */
  async reload() {
    await this.#handleMounted();
  }

  /** @override */
  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.#renderWithStyle();
    }
  }

  /** 자식의 mounted()가 비동기(Promise)인지 자동 감지하여 로딩/에러 처리 */
  async #handleMounted() {
    try {
      const result = this.mounted();
      if (result instanceof Promise) {
        this.setState({ isLoading: true, error: null });
        await result;
        this.setState({ isLoading: false });
      }
    } catch (err) {
      console.error(`[${this.constructor.name}] 마운트 에러:`, err);
      this.setState({ isLoading: false, error: err });
    }
  }

  // 상태를 변경하고 화면을 다시 그리는 커스텀 메서드 (디버그 모드 지원)
  setState(newState) {
    const prevState = { ...this.state };
    this.state = { ...this.state, ...newState };

    // 💡 디버그 모드: window.__DEBUG_COMPONENTS__ 가 true이거나 개별 컴포넌트에 debug 플래그가 있을 때 로깅
    if (window.__DEBUG_COMPONENTS__ || this.debugState) {
      console.groupCollapsed(`[State Change] <${this.tagName.toLowerCase()}>`);
      console.log(
        "%c이전 상태 (Prev):",
        "color: #94a3b8; font-weight: bold;",
        prevState,
      );
      console.log(
        "%c변경 상태 (Diff):",
        "color: #3b82f6; font-weight: bold;",
        newState,
      );
      console.log(
        "%c최종 상태 (Next):",
        "color: #10b981; font-weight: bold;",
        this.state,
      );
      console.groupEnd();
    }

    this.#renderWithStyle();
  }

  static resolveCss(fileName) {
    return `./css/components/${fileName}`;
  }

  get cssPath() {
    return null;
  }

  // 스타일시트 초기 1회 주입 및 FOUC 방지 (스타일 다운로드 완료 전 날 것의 HTML 노출 방지)
  #ensureStyles() {
    if (this.#stylesInjected) return;
    this.#stylesInjected = true;

    // ⭐️ 1. 인라인 크리티컬 CSS: 외부 CSS가 다운로드되기 전에도 스켈레톤과 기본 레이아웃이 즉시 깨짐 없이 동작하도록 보장
    const criticalStyle = document.createElement("style");
    criticalStyle.textContent = `
      :host { display: block; }
      .component-container {
        opacity: 0;
        transition: opacity 0.25s ease;
      }
      .component-container.styles-ready {
        opacity: 1;
      }
      .base-skeleton-bar {
        height: 16px;
        border-radius: 6px;
        background: linear-gradient(90deg, rgba(125,125,125,0.08) 25%, rgba(125,125,125,0.18) 50%, rgba(125,125,125,0.08) 75%);
        background-size: 200% 100%;
        animation: base-shimmer 1.6s infinite linear;
      }
      @keyframes base-shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
      }
    `;
    this.shadowRoot.appendChild(criticalStyle);

    // ⭐️ 2. 외부 CSS 링크 생성 및 로드 완료 대기
    const links = [];

    const baseLink = document.createElement("link");
    baseLink.rel = "stylesheet";
    baseLink.href = BaseComponent.resolveCss("BaseComponent.css");
    this.shadowRoot.appendChild(baseLink);
    links.push(baseLink);

    if (this.cssPath) {
      const childLink = document.createElement("link");
      childLink.rel = "stylesheet";
      childLink.href = this.cssPath;
      this.shadowRoot.appendChild(childLink);
      links.push(childLink);
    }

    const container = document.createElement("div");
    container.className = "component-container";
    this.shadowRoot.appendChild(container);

    // ⭐️ 3. CSS 로드가 완료되면 opacity: 1로 부드럽게 전환하여 FOUC 원천 차단
    let loadedCount = 0;
    const onStyleReady = () => {
      loadedCount++;
      if (loadedCount >= links.length) {
        container.classList.add("styles-ready");
      }
    };

    links.forEach((link) => {
      link.addEventListener("load", onStyleReady, { once: true });
      link.addEventListener("error", onStyleReady, { once: true }); // 오류 시에도 콘텐츠는 보여야 함
    });

    // 만약 캐시 등으로 이미 로드된 경우를 위한 안전장치
    requestAnimationFrame(() => {
      if (loadedCount >= links.length) {
        container.classList.add("styles-ready");
      }
    });
  }

  // 내부 렌더링 로직 (스타일 재파싱 방지 및 컨텐츠 영역만 업데이트)
  #renderWithStyle() {
    this.#ensureStyles();

    let html = "";

    if (this.state.error) {
      html = this.renderError(this.state.error);
    } else if (this.state.isLoading) {
      html = this.renderLoading();
    } else {
      try {
        html = this.render();
      } catch (err) {
        console.error(`[${this.constructor.name}] 렌더링 에러:`, err);
        html = this.renderError(err);
      }
    }

    const container = this.shadowRoot.querySelector(".component-container");
    if (container) {
      container.innerHTML = html;
    }

    // 로딩 및 에러 상태가 아닐 때만 이벤트 등록
    if (!this.state.isLoading && !this.state.error) {
      this.setEvents();
    }
  }

  /* --- 공통 UI 템플릿 (자식에서 필요 시 개별 오버라이드 가능) --- */

  /** 기본 스켈레톤 + 스피너 로딩 UI */
  renderLoading() {
    return `
      <div class="base-skeleton-container">
        <div class="base-skeleton-bar title"></div>
        <div class="base-skeleton-bar text"></div>
        <div class="base-skeleton-bar text short"></div>
        <div class="base-spinner-wrapper">
          <span class="base-spinner"></span>
          <span>데이터를 불러오는 중입니다...</span>
        </div>
      </div>
    `;
  }

  /** 기본 에러 UI */
  renderError(error) {
    return `
      <div class="base-error-box">
        <div class="base-error-title">⚠️ 화면을 불러오지 못했습니다.</div>
        <div class="base-error-detail">${error?.message || error}</div>
      </div>
    `;
  }

  /* --- 자식 클래스에서 오버라이드할 라이프사이클 메서드들 --- */

  /** 자식 클래스에서 오버라이드할 이벤트 등록 메서드 (optional) */
  setEvents() {}

  /** ⭐️ 데이터를 불러오거나(fetch), 초기화할 때 사용 (async 지원) */
  mounted() {}

  /** 컴포넌트가 사라질 때 타이머, 이벤트 해제 */
  unmounted() {}

  // 자식 클래스에서 이 메서드를 오버라이드하여 HTML을 반환하게 함
  render() {
    throw new Error(
      `🚨 [${this.constructor.name}] 컴포넌트에 render() 메서드가 없습니다! 오버라이드 해주세요.`,
    );
  }
}
