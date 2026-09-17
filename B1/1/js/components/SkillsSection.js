import { BaseComponent } from "./BaseComponent.js";

export class SkillsSection extends BaseComponent {
  get cssPath() {
    return BaseComponent.resolveCss("SkillsSection.css");
  }

  constructor() {
    super();
    this.categories = [
      {
        title: "Frontend Core",
        icon: "🌐",
        description: "웹 표준과 모던 자바스크립트를 기반으로 한 핵심 기술",
        skills: [
          { name: "JavaScript (ES6+)", level: "Advanced" },
          { name: "HTML5 & Semantic Web", level: "Advanced" },
          { name: "CSS3 & Flex/Grid", level: "Advanced" },
          { name: "Web Components (Shadow DOM)", level: "Intermediate" },
          { name: "TypeScript", level: "Intermediate" },
        ],
      },
      {
        title: "Architecture & Frameworks",
        icon: "🏗️",
        description: "재사용성과 관심사 분리를 위한 설계 및 도구",
        skills: [
          { name: "Component-Driven Architecture", level: "Advanced" },
          { name: "State-Driven Rendering", level: "Advanced" },
          { name: "React / Vite", level: "Intermediate" },
          { name: "Mobile First Responsive Web", level: "Advanced" },
        ],
      },
      {
        title: "Tools & DevOps",
        icon: "🛠️",
        description: "효율적인 협업과 지속 가능한 배포 환경",
        skills: [
          { name: "Git & GitHub", level: "Intermediate" },
          { name: "GitHub Pages", level: "Intermediate" },
          { name: "Chrome DevTools Debugging", level: "Advanced" },
          { name: "REST API Integration", level: "Intermediate" },
        ],
      },
    ];
  }

  render() {
    return `
      <section class="skills-container">
        <h2 class="section-title">Skills & Capabilities</h2>
        <p class="section-desc">
          지속 가능한 코드와 견고한 사용자 경험을 만들기 위해 활용하는 기술 스택입니다.
        </p>

        <div class="skills-grid">
          ${this.categories
            .map(
              ({ title, icon, description, skills }) => `
            <article class="skill-category-card">
              <div class="category-header">
                <span class="category-icon">${icon}</span>
                <div>
                  <h3 class="category-title">${title}</h3>
                  <p class="category-desc">${description}</p>
                </div>
              </div>
              <ul class="skill-tags">
                ${skills
                  .map(
                    (skill) => `
                  <li class="skill-badge">
                    <span class="skill-name">${skill.name}</span>
                    <span class="skill-level">${skill.level}</span>
                  </li>
                `
                  )
                  .join("")}
              </ul>
            </article>
          `
            )
            .join("")}
        </div>
      </section>
    `;
  }
}

customElements.define("skills-section", SkillsSection);
