/**
 * main.js - 애플리케이션 진입점 및 전역 컨트롤러
 */

// 1. 웹 컴포넌트 등록
import "./components/HeroSection.js";
import "./components/GreetingsText.js";
import "./components/CtaButton.js";
import "./components/AboutSection.js";
import "./components/SkillsSection.js";
import "./components/ProjectsSection.js";
import "./components/ContactSection.js";

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initNavigation();
  initScrollEffects();
  initIntersectionObserver();
  initCtaButton();
});

/**
 * 2. 다크 모드 컨트롤러 (요구사항 3, 10)
 * - 시스템 설정(prefers-color-scheme) 감지
 * - localStorage 영속성 유지
 */
function initTheme() {
  const themeToggleBtn = document.querySelector("#theme-toggle");
  const themeIcon = themeToggleBtn?.querySelector(".theme-icon");
  const THEME_STORAGE_KEY = "portfolio_theme";

  // 시스템 다크모드 선호 여부
  const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
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

  // 시스템 설정 실시간 변경 감지
  window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
    if (!localStorage.getItem(THEME_STORAGE_KEY)) {
      applyTheme(e.matches ? "dark" : "light");
    }
  });
}

/**
 * 3. 네비게이션 & 햄버거 메뉴 컨트롤러 (요구사항 1, 4, 5)
 */
function initNavigation() {
  const hamburgerBtn = document.querySelector("#hamburger-btn");
  const navLinks = document.querySelector("#nav-links");
  const navItems = document.querySelectorAll(".nav-link");

  // 햄버거 메뉴 토글
  hamburgerBtn?.addEventListener("click", () => {
    const isActive = hamburgerBtn.classList.toggle("active");
    navLinks?.classList.toggle("active", isActive);
  });

  // 모바일 메뉴 클릭 시 자동 닫힘
  navItems.forEach((link) => {
    link.addEventListener("click", () => {
      hamburgerBtn?.classList.remove("active");
      navLinks?.classList.remove("active");
    });
  });
}

/**
 * 4. 스크롤 인터랙션 컨트롤러 (요구사항 15, 20)
 * - 60px 이상 스크롤 시 헤더 배경색 변경
 * - 300px 이상 스크롤 시 스크롤 탑 버튼 노출
 */
function initScrollEffects() {
  const header = document.querySelector("#main-header");
  const scrollTopBtn = document.querySelector("#scroll-top-btn");

  window.addEventListener("scroll", () => {
    const scrollY = window.scrollY;

    // 헤더 배경 블러/색상 전환 (60px 이상)
    if (header) {
      header.classList.toggle("scrolled", scrollY > 60);
    }

    // 스크롤 탑 버튼 가시성 (300px 이상)
    if (scrollTopBtn) {
      scrollTopBtn.classList.toggle("visible", scrollY > 300);
    }
  });

  // 스크롤 탑 버튼 클릭 시 부드럽게 상단 이동
  scrollTopBtn?.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });
}

/**
 * 5. Intersection Observer (요구사항 5, 6, 26)
 * - threshold: 0.2 이상 권장
 * - 섹션 스크롤 진입 애니메이션 (.reveal)
 * - 현재 보고 있는 섹션 메뉴 하이라이트
 */
function initIntersectionObserver() {
  const sections = document.querySelectorAll("main section");
  const navLinks = document.querySelectorAll(".nav-link");

  const observerOptions = {
    root: null,
    threshold: 0.25, // 0.2 이상 권장 만족
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        // 스크롤 진입 애니메이션 활성화
        entry.target.classList.add("active");

        // 네비게이션 현재 메뉴 하이라이트
        const currentId = entry.target.getAttribute("id");
        navLinks.forEach((link) => {
          const href = link.getAttribute("href");
          if (href === `#${currentId}`) {
            link.classList.add("active");
          } else {
            link.classList.remove("active");
          }
        });
      }
    });
  }, observerOptions);

  sections.forEach((section) => observer.observe(section));
}

/**
 * 6. CTA 버튼 스크롤 연동
 */
function initCtaButton() {
  const ctaBtn = document.querySelector("cta-button");
  ctaBtn?.addEventListener("click", () => {
    const projectsSection = document.querySelector("#projects");
    projectsSection?.scrollIntoView({ behavior: "smooth" });
  });
}
