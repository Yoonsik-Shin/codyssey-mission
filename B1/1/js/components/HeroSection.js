import { BaseComponent } from "./BaseComponent.js";

/**
 * 인사말, CTA 버튼이 포함되어
 */
export class HeroSection extends BaseComponent {
  get cssPath() {
    return BaseComponent.resolveCss("HeroSection.css");
  }

  render() {
    return `
      <section class="hero-container">
        <slot></slot>
      </section>  
    `;
  }
}

customElements.define("hero-section", HeroSection);
