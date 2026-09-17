import { BaseComponent } from "./BaseComponent.js";

/** 자기소개 + 프로필 이미지 */
export class AboutSection extends BaseComponent {
  get cssPath() {
    return BaseComponent.resolveCss("AboutSection.css");
  }

  render() {
    return `
      <section class="about-container">
        <h2 class="section-title">About Me</h2>
        <div class="about-content">
          <div class="profile-image-wrapper">
            <img 
              src="./images/profile.jpg" 
              alt="개발자 신윤식 프로필 사진" 
              class="profile-img" 
            />
          </div>
          <div class="about-text">
            <h3 class="about-subtitle">성장과 협업을 즐기는 개발자 신윤식입니다</h3>
            <p class="about-description">
              문제를 해결할 때 단순히 당장 동작하는 코드를 넘어, <strong>근본 원인을 파악하고 재사용 가능한 구조로 설계하는 것</strong>을 중요하게 생각합니다.
            </p>
            <p class="about-description">
              브라우저 표준 기술인 웹 컴포넌트(Web Components)와 모던 자바스크립트 아키텍처에 깊은 관심을 가지고 있으며, 항상 읽기 쉽고 확장성 높은 코드를 작성합니다.
            </p>
            
            <div class="about-cards">
              <div class="about-card">
                <span class="card-icon">🎯</span>
                <div class="card-text">
                  <h4>핵심 가치</h4>
                  <p>근본적인 원인 해결 & 컴포넌트 추상화</p>
                </div>
              </div>

              <div class="about-card">
                <span class="card-icon">⚡</span>
                <div class="card-text">
                  <h4>관심 분야</h4>
                  <p>Web Components, 반응형 UI, 성능 최적화</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    `;
  }
}

customElements.define("about-section", AboutSection);
