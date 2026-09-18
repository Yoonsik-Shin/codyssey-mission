/**
 * theme.js - 다크 모드 및 테마 전환 컨트롤러 (요구사항 3, 10)
 * - 테마 결정 우선순위:
 *   1순위: localStorage에 저장된 사용자 명시적 선택 테마 (다크/라이트)
 *   2순위: 시스템(OS) 설정 (prefers-color-scheme: dark)
 *   3순위: 시스템 기본값 (light)
 */
export function initTheme() {
  const themeToggleBtn = document.querySelector("#theme-toggle");
  const themeIcon = themeToggleBtn?.querySelector(".theme-icon");
  const THEME_STORAGE_KEY = "portfolio_theme";

  // 시스템 다크모드 선호 여부
  const systemPrefersDark = window.matchMedia(
    "(prefers-color-scheme: dark)",
  ).matches;
  const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
  const initialTheme = savedTheme || (systemPrefersDark ? "dark" : "light");

  const applyTheme = (theme) => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_STORAGE_KEY, theme);
    if (themeIcon) {
      themeIcon.textContent = theme === "dark" ? "☀️" : "🌙";
    }
  };

  applyTheme(initialTheme);

  // 토글 버튼 클릭 이벤트
  themeToggleBtn?.addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const nextTheme = currentTheme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
  });

  // 시스템 설정 실시간 변경 감지 (사용자가 웹에서 수동 변경한 적 없을 때만 OS 설정 동기화)
  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", (e) => {
      if (!localStorage.getItem(THEME_STORAGE_KEY)) {
        applyTheme(e.matches ? "dark" : "light");
      }
    });
}
