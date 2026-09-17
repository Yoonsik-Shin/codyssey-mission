import { BaseComponent } from "./BaseComponent.js";

export class CtaButton extends BaseComponent {
  get cssPath() {
    return BaseComponent.resolveCss("CtaButton.css");
  }

  render() {
    return `
      <button class="cta-btn">
        <slot></slot>
      </button>
    `;
  }
}

customElements.define("cta-button", CtaButton);
