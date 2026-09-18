import { BaseComponent } from "./BaseComponent.js";

/**
 * HeroSection
 * - 타자기 효과(Typewriter Effect)
 * - 슬로건 및 소개 문구
 * - Projects 섹션으로 이동하는 CTA 버튼 통합
 */
export class HeroSection extends BaseComponent {
  get cssPath() {
    return BaseComponent.resolveCss("HeroSection.css");
  }

  // 🔒 Private 필드 선언
  #phrases = [
    "안녕하세요! 개발자 신윤식입니다. 👋",
    "사용자 경험과 깔끔한 코드를 고민합니다. 🚀",
    "웹 컴포넌트로 만드는 모던 웹 애플리케이션. 💡",
  ];
  #phraseIndex = 0;
  #charIndex = 0;
  #isDeleting = false;
  #timer = null;

  mounted() {
    this.#runTypewriterEffect();
  }

  unmounted() {
    if (this.#timer) {
      clearTimeout(this.#timer);
    }
  }

  // 타자기 효과 실행
  #runTypewriterEffect() {
    const textEl = this.shadowRoot.querySelector(".typewriter-text");
    if (!textEl) return;

    const currentPhrase = this.#phrases[this.#phraseIndex];

    if (this.#isDeleting) {
      this.#charIndex--;
    } else {
      this.#charIndex++;
    }

    textEl.textContent = currentPhrase.substring(0, this.#charIndex);

    let speed = this.#isDeleting ? 40 : 80;

    if (!this.#isDeleting && this.#charIndex === currentPhrase.length) {
      speed = 1800; // 한 문장 완료 후 대기
      this.#isDeleting = true;
    } else if (this.#isDeleting && this.#charIndex === 0) {
      this.#isDeleting = false;
      this.#phraseIndex = (this.#phraseIndex + 1) % this.#phrases.length;
      speed = 400;
    }

    this.#timer = setTimeout(() => this.#runTypewriterEffect(), speed);
  }

  setEvents() {
    // CTA 버튼 클릭 시 Projects 섹션으로 부드럽게 스크롤
    const ctaBtn = this.shadowRoot.querySelector(".cta-btn");
    ctaBtn?.addEventListener("click", (e) => {
      e.preventDefault();
      const target = document.querySelector("#projects");
      target?.scrollIntoView({ behavior: "smooth" });
    });
  }

  render() {
    return `
      <section class="hero-container">
        <div class="intro-content">
          <span class="greeting-badge">Front-End Developer</span>
          <h1 class="greeting-headline">
            <span class="typewriter-text"></span>
            <span class="cursor" aria-hidden="true">|</span>
          </h1>
          <p class="greeting-sub">
            웹 표준(Web Components)과 모던 자바스크립트로 견고하고 사용자 친화적인 웹 인터페이스를 만듭니다.
          </p>
        </div>

        <a href="#projects" class="cta-btn">
          내 프로젝트 보러가기 🚀
        </a>
      </section>
    `;
  }
}

customElements.define("hero-section", HeroSection);
