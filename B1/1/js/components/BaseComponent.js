export class BaseComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.state = {
      isLoading: false,
      error: null,
    };
    this._isMounted = false;
  }

  // 어떤 속성(attribute)을 감시할지 브라우저에게 알려줌 (자식 클래스에서 오버라이딩)
  static get observedAttributes() {
    return [];
  }

  /** @override */
  connectedCallback() {
    this._renderWithStyle();

    if (!this._isMounted) {
      this._isMounted = true;
      this._handleMounted();
    }
  }

  /** @override */
  disconnectedCallback() {
    this.unmounted();
  }

  /** @override */
  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this._renderWithStyle();
    }
  }

  /** 자식의 mounted()가 비동기(Promise)인지 자동 감지하여 로딩/에러 처리 */
  async _handleMounted() {
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

  // 상태를 변경하고 화면을 다시 그리는 커스텀 메서드
  setState(newState) {
    this.state = { ...this.state, ...newState };
    this._renderWithStyle();
  }

  static resolveCss(fileName) {
    return `./css/components/${fileName}`;
  }

  get cssPath() {
    return null;
  }

  // 스타일시트 초기 1회 주입
  _ensureStyles() {
    if (this._stylesInjected) return;
    this._stylesInjected = true;

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

  // 내부 렌더링 로직 (스타일 재파싱 방지 및 컨텐츠 영역만 업데이트)
  _renderWithStyle() {
    this._ensureStyles();

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
