import { BaseComponent } from "./BaseComponent.js";

export class GreetingsText extends BaseComponent {
  get cssPath() {
    return BaseComponent.resolveCss("GreetingsText.css");
  }

  constructor() {
    super();
    this.phrases = [
      "안녕하세요! 개발자 신윤식입니다. 👋",
      "사용자 경험과 깔끔한 코드를 고민합니다. 🚀",
      "웹 컴포넌트로 만드는 모던 웹 애플리케이션. 💡",
    ];
    this.phraseIndex = 0;
    this.charIndex = 0;
    this.isDeleting = false;
    this.timer = null;
  }

  mounted() {
    this.type();
  }

  unmounted() {
    if (this.timer) {
      clearTimeout(this.timer);
    }
  }

  type() {
    const textEl = this.shadowRoot.querySelector(".typewriter-text");
    if (!textEl) return;

    const currentPhrase = this.phrases[this.phraseIndex];

    if (this.isDeleting) {
      this.charIndex--;
    } else {
      this.charIndex++;
    }

    textEl.textContent = currentPhrase.substring(0, this.charIndex);

    let speed = this.isDeleting ? 40 : 80;

    if (!this.isDeleting && this.charIndex === currentPhrase.length) {
      speed = 1800; // 한 문장 완료 후 잠시 대기
      this.isDeleting = true;
    } else if (this.isDeleting && this.charIndex === 0) {
      this.isDeleting = false;
      this.phraseIndex = (this.phraseIndex + 1) % this.phrases.length;
      speed = 400;
    }

    this.timer = setTimeout(() => this.type(), speed);
  }

  render() {
    return `
      <div class="intro-container">
        <span class="greeting-badge">Front-End Developer</span>
        <h1 class="greeting-headline">
          <span class="typewriter-text"></span>
          <span class="cursor" aria-hidden="true">|</span>
        </h1>
        <p class="greeting-sub">
          웹 표준(Web Components)과 모던 자바스크립트로 견고하고 사용자 친화적인 웹 인터페이스를 만듭니다.
        </p>
      </div>
    `;
  }
}

customElements.define("greetings-text", GreetingsText);
