import { BaseComponent } from "./BaseComponent.js";

/**
 * [Internal View Helper 1] 성공 피드백 뷰
 * - 메시지 전송 성공 시의 UI 렌더링 및 재작성 버튼 이벤트 바인딩 전담
 */
class ContactSuccessView {
  static render(email) {
    return `
      <div class="success-box">
        <span class="success-icon">🎉</span>
        <h3 class="success-title">메시지가 성공적으로 전송되었습니다!</h3>
        <p class="success-desc">확인 후 남겨주신 이메일(${email})로 회신드리겠습니다.</p>
        <button id="reset-form-btn" class="reset-btn">새로운 메시지 작성하기</button>
      </div>
    `;
  }

  static bindEvents(shadowRoot, onReset) {
    const resetBtn = shadowRoot.querySelector("#reset-form-btn");
    resetBtn?.addEventListener("click", onReset);
  }
}

/**
 * [Internal View Helper 2] 폼 입력 뷰
 * - 입력 필드(이름, 이메일, 메시지), 에러 텍스트 노출 및 실시간/제출 이벤트 바인딩 전담
 */
class ContactFormView {
  static render(formData, errors, isSubmitting) {
    return `
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
            aria-invalid="${errors.name ? "true" : "false"}"
            required 
          />
          <span id="error-name" class="error-text" role="alert" aria-live="polite">${errors.name}</span>
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
            aria-invalid="${errors.email ? "true" : "false"}"
            required 
          />
          <span id="error-email" class="error-text" role="alert" aria-live="polite">${errors.email}</span>
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
            aria-invalid="${errors.message ? "true" : "false"}"
            required
          >${formData.message}</textarea>
          <span id="error-message" class="error-text" role="alert" aria-live="polite">${errors.message}</span>
        </div>

        <!-- 제출 버튼 -->
        <button type="submit" class="submit-btn" ${isSubmitting ? "disabled" : ""}>
          ${isSubmitting ? "전송 중..." : "메시지 보내기 🚀"}
        </button>
      </form>
    `;
  }

  static bindEvents(shadowRoot, { onInput, onSubmit }) {
    const form = shadowRoot.querySelector("#contact-form");
    if (!form) return;

    ["name", "email", "message"].forEach((field) => {
      const el = shadowRoot.querySelector(`#${field}`);
      el?.addEventListener("input", (e) => onInput(field, e.target.value));
    });

    form.addEventListener("submit", onSubmit);
  }

  // 에러 메시지 및 인풋 상태 미세 DOM 업데이트 (리플로우 방지)
  static updateErrors(shadowRoot, errors) {
    let firstErrorField = null;

    ["name", "email", "message"].forEach((field) => {
      const errorEl = shadowRoot.querySelector(`#error-${field}`);
      const inputEl = shadowRoot.querySelector(`#${field}`);
      const hasError = Boolean(errors[field]);

      if (errorEl) {
        errorEl.textContent = errors[field] || "";
      }

      if (inputEl) {
        inputEl.classList.toggle("invalid", hasError);
        inputEl.setAttribute("aria-invalid", hasError ? "true" : "false");
        if (hasError && !firstErrorField) {
          firstErrorField = inputEl;
        }
      }
    });

    if (firstErrorField) {
      firstErrorField.focus();
    }
  }

  static clearFieldError(shadowRoot, fieldName) {
    const errorEl = shadowRoot.querySelector(`#error-${fieldName}`);
    const inputEl = shadowRoot.querySelector(`#${fieldName}`);
    if (errorEl) errorEl.textContent = "";
    if (inputEl) {
      inputEl.classList.remove("invalid");
      inputEl.setAttribute("aria-invalid", "false");
    }
  }
}

/**
 * [Main Controller Component] ContactSection
 * - 폼 상태(state) 관리 및 Formspree API 비동기 통신 총괄
 */
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
    if (this.state.isSubmitted) {
      ContactSuccessView.bindEvents(this.shadowRoot, () => this.#handleReset());
    } else {
      ContactFormView.bindEvents(this.shadowRoot, {
        onInput: (field, value) => this.#handleInput(field, value),
        onSubmit: (e) => this.#handleSubmit(e),
      });
    }
  }

  #handleInput(field, value) {
    this.state.formData[field] = value;
    ContactFormView.clearFieldError(this.shadowRoot, field);
  }

  #handleReset() {
    this.setState({
      formData: { name: "", email: "", message: "" },
      errors: { name: "", email: "", message: "" },
      isSubmitting: false,
      isSubmitted: false,
    });
  }

  #validateForm() {
    const { name, email, message } = this.state.formData;
    const errors = { name: "", email: "", message: "" };
    let isValid = true;

    if (!name.trim()) {
      errors.name = "이름을 입력해주세요.";
      isValid = false;
    } else if (name.trim().length < 2) {
      errors.name = "이름은 최소 2글자 이상이어야 합니다.";
      isValid = false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email.trim()) {
      errors.email = "이메일을 입력해주세요.";
      isValid = false;
    } else if (!emailRegex.test(email.trim())) {
      errors.email = "올바른 이메일 형식(example@domain.com)을 입력해주세요.";
      isValid = false;
    }

    if (!message.trim()) {
      errors.message = "문의 내용을 입력해주세요.";
      isValid = false;
    } else if (message.trim().length < 5) {
      errors.message = "문의 내용은 최소 5글자 이상 작성해주세요.";
      isValid = false;
    }

    return { isValid, errors };
  }

  static #DEFAULT_ENDPOINT = "https://formspree.io/f/myezyrkk";

  async #handleSubmit(event) {
    event.preventDefault();

    const { isValid, errors } = this.#validateForm();

    if (!isValid) {
      this.state.errors = errors;
      ContactFormView.updateErrors(this.shadowRoot, errors);
      return;
    }

    this.state.errors = { name: "", email: "", message: "" };
    ContactFormView.updateErrors(this.shadowRoot, this.state.errors);
    this.setState({ isSubmitting: true });

    const endpoint =
      this.getAttribute("endpoint") || ContactSection.#DEFAULT_ENDPOINT;

    try {
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
              ? ContactSuccessView.render(formData.email)
              : ContactFormView.render(formData, errors, isSubmitting)
          }
        </div>
      </section>
    `;
  }
}

customElements.define("contact-section", ContactSection);
