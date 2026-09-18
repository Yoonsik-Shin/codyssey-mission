/**
 * main.js - 애플리케이션 진입점 (App Entrypoint)
 * - 웹 컴포넌트 등록 및 전역 컨트롤러 초기화 조율
 */

// 1. 웹 컴포넌트 등록
import "./components/HeroSection.js";
import "./components/AboutSection.js";
import "./components/SkillsSection.js";
import "./components/ProjectsSection.js";
import "./components/ContactSection.js";

// 2. 전역 UI 인터랙션 컨트롤러
import { initTheme } from "./controllers/theme.js";
import { initNavigation } from "./controllers/navigation.js";
import {
  initScrollEffects,
  initIntersectionObserver,
} from "./controllers/scroll.js";

// 3. 애플리케이션 부트스트랩
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initNavigation();
  initScrollEffects();
  initIntersectionObserver();
});
