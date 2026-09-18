import { BaseComponent } from "./BaseComponent.js";

export class ProjectsSection extends BaseComponent {
  get cssPath() {
    return BaseComponent.resolveCss("ProjectsSection.css");
  }

  constructor() {
    super();
    this.state = {
      ...this.state,
      repos: [],
      languages: ["All"],
      selectedLanguage: "All",
    };
  }

  // 캐시 설정 상수
  static #CACHE_EXPIRE = 1000 * 60 * 5; // 5분 캐시

  async mounted() {
    await this.#fetchRepositories();
  }

  // GitHub 저장소 데이터 호출
  async #fetchRepositories() {
    const username = this.getAttribute("username") || "Yoonsik-Shin";
    const CACHE_KEY = `github_repos_${username}`;
    const CACHE_TIME_KEY = `${CACHE_KEY}_time`;

    // 1. 세션 캐시 확인
    const cachedData = sessionStorage.getItem(CACHE_KEY);
    const cachedTime = sessionStorage.getItem(CACHE_TIME_KEY);

    if (
      cachedData &&
      cachedTime &&
      Date.now() - Number(cachedTime) < ProjectsSection.#CACHE_EXPIRE
    ) {
      const repos = JSON.parse(cachedData);
      this.#updateRepoState(repos);
      return;
    }

    // 2. GitHub API 호출
    try {
      const res = await fetch(
        `https://api.github.com/users/${username}/repos?sort=updated&per_page=12`,
      );

      if (!res.ok) {
        if (res.status === 403) {
          throw new Error(
            "GitHub API 요청 횟수(60회/시간)를 초과했습니다. 잠시 후 다시 시도해주세요.",
          );
        }
        throw new Error(
          `저장소 목록을 불러오지 못했습니다. (상태 코드: ${res.status})`,
        );
      }

      const data = await res.json();
      const ownRepos = data.filter((repo) => !repo.fork);

      // 캐시 저장
      sessionStorage.setItem(CACHE_KEY, JSON.stringify(ownRepos));
      sessionStorage.setItem(CACHE_TIME_KEY, String(Date.now()));

      this.#updateRepoState(ownRepos);
    } catch (err) {
      console.error("[ProjectsSection] API 에러:", err);
      throw err; // BaseComponent error boundary가 캐치
    }
  }

  // 메서드: 상태 업데이트
  #updateRepoState(repos) {
    const langs = [
      "All",
      ...new Set(repos.map((r) => r.language).filter(Boolean)),
    ];

    this.setState({
      repos,
      languages: langs,
      selectedLanguage: "All",
    });
  }

  setEvents() {
    // 1. 언어 필터 버튼 이벤트
    const filterButtons = this.shadowRoot.querySelectorAll(".filter-btn");
    filterButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const lang = btn.getAttribute("data-lang");
        this.setState({ selectedLanguage: lang });
      });
    });

    // 2. 재시도 버튼 이벤트 (에러 상태일 때)
    const retryBtn = this.shadowRoot.querySelector("#retry-btn");
    if (retryBtn) {
      retryBtn.addEventListener("click", async () => {
        sessionStorage.clear();
        this.setState({ isLoading: true, error: null });
        try {
          await this.#fetchRepositories();
          this.setState({ isLoading: false });
        } catch (err) {
          this.setState({ isLoading: false, error: err });
        }
      });
    }
  }

  renderLoading() {
    return `
      <section class="projects-container">
        <div class="projects-header">
          <div>
            <h2 class="section-title">Projects</h2>
            <p class="section-desc">GitHub 저장소에서 최신 프로젝트 목록을 불러오는 중입니다...</p>
          </div>
        </div>
        <div class="projects-grid">
          ${Array.from({ length: 6 })
            .map(
              () => `
            <div class="project-card" style="pointer-events: none;">
              <div class="base-skeleton-bar title" style="margin-bottom: 16px; width: 60%;"></div>
              <div class="base-skeleton-bar text" style="margin-bottom: 8px;"></div>
              <div class="base-skeleton-bar text short" style="margin-bottom: 24px;"></div>
              <div style="display: flex; justify-content: space-between; margin-top: auto; padding-top: 14px; border-top: 1px solid var(--border-color, #f1f5f9);">
                <div class="base-skeleton-bar" style="width: 50px; height: 20px; border-radius: 9999px;"></div>
                <div class="base-skeleton-bar" style="width: 70px; height: 16px;"></div>
              </div>
            </div>
          `,
            )
            .join("")}
        </div>
      </section>
    `;
  }

  renderError(error) {
    return `
      <section class="projects-container">
        <h2 class="section-title">Projects</h2>
        <div class="projects-error-box">
          <span class="error-icon">⚠️</span>
          <p class="error-message">프로젝트를 불러올 수 없습니다.</p>
          <small class="error-detail">${error.message || error}</small>
          <button id="retry-btn" class="retry-btn">다시 시도</button>
        </div>
      </section>
    `;
  }

  render() {
    const { repos, languages, selectedLanguage } = this.state;

    // 언어별 필터링
    const filteredRepos =
      selectedLanguage === "All"
        ? repos
        : repos.filter((repo) => repo.language === selectedLanguage);

    return `
      <section class="projects-container">
        <div class="projects-header">
          <div>
            <h2 class="section-title">Projects</h2>
            <p class="section-desc">GitHub 저장소에서 실시간으로 연동된 최신 프로젝트 목록입니다.</p>
          </div>

          <!-- 언어 필터 버튼 목록 (요구사항 24) -->
          ${
            languages.length > 1
              ? `
            <div class="filter-group">
              ${languages
                .map(
                  (lang) => `
                <button 
                  class="filter-btn ${lang === selectedLanguage ? "active" : ""}" 
                  data-lang="${lang}"
                >
                  ${lang}
                </button>
              `,
                )
                .join("")}
            </div>
          `
              : ""
          }
        </div>

        ${
          filteredRepos.length === 0
            ? `
          <div class="empty-box">
            <span class="empty-icon">📂</span>
            <p class="empty-message">표시할 프로젝트가 없습니다.</p>
          </div>
        `
            : `
          <div class="projects-grid">
            ${filteredRepos
              .map(
                ({
                  name,
                  html_url,
                  description,
                  language,
                  stargazers_count,
                }) => `
              <a href="${html_url}" target="_blank" rel="noopener noreferrer" class="project-card">
                <div class="card-header">
                  <h3 class="repo-name">${name}</h3>
                  <span class="stars" title="Stars">⭐ ${stargazers_count}</span>
                </div>
                <p class="repo-desc">${description || "등록된 프로젝트 설명이 없습니다."}</p>
                <div class="repo-footer">
                  ${language ? `<span class="language-badge">${language}</span>` : "<span></span>"}
                  <span class="view-link">View Repo ↗</span>
                </div>
              </a>
            `,
              )
              .join("")}
          </div>
        `
        }
      </section>
    `;
  }
}

customElements.define("project-section", ProjectsSection);
