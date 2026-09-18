import { BaseComponent } from "./BaseComponent.js";

export class ContactSection extends BaseComponent {
  get cssPath() {
    return BaseComponent.resolveCss("ContactSection.css");
  }

  constructor() {
    super();
    this.state = {
      formData: {
        name: "",
        email: "",
        message: "",
      },
      errors: {
        name: "",
        email: "",
        message: "",
      },
      isSubmitting: false,
      isSubmitted: false,
    };
  }

  setEvents() {
    // 1. 다시 작성하기 버튼 이벤트 (성공 화면일 때)
    const resetBtn = this.shadowRoot.querySelector("#reset-form-btn");
    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        this.setState({
          formData: { name: "", email: "", message: "" },
          errors: { name: "", email: "", message: "" },
          isSubmitting: false,
          isSubmitted: false,
        });
      });
      return; // 성공 화면일 때는 아래 폼 리스너 등록 생략
    }

    // 2. 폼 입력 및 제출 이벤트 (입력 화면일 때)
    const form = this.shadowRoot.querySelector("#contact-form");
    if (!form) return;

    // 실시간 input 유효성 검사
    const nameInput = this.shadowRoot.querySelector("#name");
    const emailInput = this.shadowRoot.querySelector("#email");
    const messageInput = this.shadowRoot.querySelector("#message");

    if (nameInput) {
      nameInput.addEventListener("input", (e) => {
        this.state.formData.name = e.target.value;
        this.#clearFieldError("name");
      });
    }

    if (emailInput) {
      emailInput.addEventListener("input", (e) => {
        this.state.formData.email = e.target.value;
        this.#clearFieldError("email");
      });
    }

    if (messageInput) {
      messageInput.addEventListener("input", (e) => {
        this.state.formData.message = e.target.value;
        this.#clearFieldError("message");
      });
    }

    // 폼 제출 이벤트
    form.addEventListener("submit", (e) => this.#handleSubmit(e));
  }

  // 특정 필드 에러 초기화
  #clearFieldError(fieldName) {
    const errorEl = this.shadowRoot.querySelector(`#error-${fieldName}`);
    const inputEl = this.shadowRoot.querySelector(`#${fieldName}`);
    if (errorEl) errorEl.textContent = "";
    if (inputEl) inputEl.classList.remove("invalid");
  }

  // 폼 입력값 유효성 검증
  #validateForm() {
    const { name, email, message } = this.state.formData;
    const errors = { name: "", email: "", message: "" };
    let isValid = true;

    // 1. 이름 검증 (필수값 & 최소 길이)
    if (!name.trim()) {
      errors.name = "이름을 입력해주세요.";
      isValid = false;
    } else if (name.trim().length < 2) {
      errors.name = "이름은 최소 2글자 이상이어야 합니다.";
      isValid = false;
    }

    // 2. 이메일 검증 (필수값 & 형식)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email.trim()) {
      errors.email = "이메일을 입력해주세요.";
      isValid = false;
    } else if (!emailRegex.test(email.trim())) {
      errors.email = "올바른 이메일 형식(example@domain.com)을 입력해주세요.";
      isValid = false;
    }

    // 3. 메시지 검증 (필수값 & 최소 길이)
    if (!message.trim()) {
      errors.message = "문의 내용을 입력해주세요.";
      isValid = false;
    } else if (message.trim().length < 5) {
      errors.message = "문의 내용은 최소 5글자 이상 작성해주세요.";
      isValid = false;
    }

    return { isValid, errors };
  }

  // 에러 메시지 돔 미세 업데이트 (전체 innerHTML 재파싱 방지)
  #applyErrorsToDom(errors) {
    ["name", "email", "message"].forEach((field) => {
      const errorEl = this.shadowRoot.querySelector(`#error-${field}`);
      const inputEl = this.shadowRoot.querySelector(`#${field}`);
      if (errorEl) errorEl.textContent = errors[field] || "";
      if (inputEl) {
        inputEl.classList.toggle("invalid", Boolean(errors[field]));
      }
    });
  }

  // 기본 Formspree 엔드포인트 상수
  static #DEFAULT_ENDPOINT = "https://formspree.io/f/myezyrkk";

  // 폼 제출 핸들러
  async #handleSubmit(event) {
    event.preventDefault(); // 기본 폼 제출 동작 방지 (요구사항 17)

    const { isValid, errors } = this.#validateForm();

    if (!isValid) {
      this.state.errors = errors;
      this.#applyErrorsToDom(errors);
      return;
    }

    this.state.errors = { name: "", email: "", message: "" };
    this.#applyErrorsToDom(this.state.errors);
    this.setState({ isSubmitting: true });

    // HTML 속성(endpoint)에서 주입받거나 기본값 사용 (하드코딩 분리)
    const endpoint =
      this.getAttribute("endpoint") || ContactSection.#DEFAULT_ENDPOINT;

    try {
      // Formspree 실제 이메일 전송 API 호출 (보너스 요구사항 충족)
      const res = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(this.state.formData),
      });

      if (!res.ok) {
        throw new Error(`이메일 전송 실패 (상태 코드: ${res.status})`);
      }

      this.setState({
        isSubmitting: false,
        isSubmitted: true,
      });
    } catch (err) {
      console.error("[ContactSection] 전송 실패:", err);
      this.setState({
        isSubmitting: false,
        errors: {
          message: "메시지 전송 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.",
        },
      });
    }
  }

  render() {
    const { formData, errors, isSubmitting, isSubmitted } = this.state;

    return `
      <section class="contact-container">
        <h2 class="section-title">Contact</h2>
        <p class="section-desc">프로젝트 문의나 협업 제안 등 편하게 메시지를 남겨주세요.</p>

        <div class="contact-card">
          ${
            isSubmitted
              ? `
            <div class="success-box">
              <span class="success-icon">🎉</span>
              <h3 class="success-title">메시지가 성공적으로 전송되었습니다!</h3>
              <p class="success-desc">확인 후 남겨주신 이메일(${formData.email})로 회신드리겠습니다.</p>
              <button id="reset-form-btn" class="reset-btn">새로운 메시지 작성하기</button>
            </div>
          `
              : `
            <form id="contact-form" class="contact-form" novalidate>
              <!-- 이름 입력 필드 -->
              <div class="form-group">
                <label for="name" class="form-label">
                  이름 <span class="required">*</span>
                </label>
                <input 
                  type="text" 
                  id="name" 
                  name="name" 
                  class="form-input ${errors.name ? "invalid" : ""}" 
                  placeholder="홍길동"
                  value="${formData.name}"
                  required 
                />
                <span id="error-name" class="error-text">${errors.name}</span>
              </div>

              <!-- 이메일 입력 필드 -->
              <div class="form-group">
                <label for="email" class="form-label">
                  이메일 주소 <span class="required">*</span>
                </label>
                <input 
                  type="email" 
                  id="email" 
                  name="email" 
                  class="form-input ${errors.email ? "invalid" : ""}" 
                  placeholder="example@domain.com"
                  value="${formData.email}"
                  required 
                />
                <span id="error-email" class="error-text">${errors.email}</span>
              </div>

              <!-- 메시지 입력 필드 -->
              <div class="form-group">
                <label for="message" class="form-label">
                  문의 내용 <span class="required">*</span>
                </label>
                <textarea 
                  id="message" 
                  name="message" 
                  class="form-textarea ${errors.message ? "invalid" : ""}" 
                  rows="5" 
                  placeholder="궁금한 점이나 제안하고 싶으신 내용을 자유롭게 작성해주세요."
                  required
                >${formData.message}</textarea>
                <span id="error-message" class="error-text">${errors.message}</span>
              </div>

              <!-- 제출 버튼 -->
              <button type="submit" class="submit-btn" ${isSubmitting ? "disabled" : ""}>
                ${isSubmitting ? "전송 중..." : "메시지 보내기 🚀"}
              </button>
            </form>
          `
          }
        </div>
      </section>
    `;
  }
}

customElements.define("contact-section", ContactSection);
