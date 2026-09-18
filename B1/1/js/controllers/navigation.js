/**
 * navigation.js - 네비게이션 & 햄버거 메뉴 컨트롤러 (요구사항 1, 4, 5)
 */
export function initNavigation() {
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
