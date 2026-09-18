/**
 * scroll.js - 스크롤 인터랙션 및 Intersection Observer 컨트롤러 (요구사항 5, 6, 15, 20, 26)
 */

/**
 * 스크롤 인터랙션 컨트롤러 (헤더 블러, 스크롤탑 버튼)
 * 💡 임계값(Threshold) 설계 기준:
 * - 60px: 기본 헤더 높이(70px) 직전에 글래스모피즘(블러+경계선)으로 자연스럽게 전환
 * - 300px: 사용자가 Hero 섹션을 완전히 벗어나 스크롤했을 때 비로소 상단 이동 버튼 노출
 */
export function initScrollEffects() {
  const header = document.querySelector("#main-header");
  const scrollTopBtn = document.querySelector("#scroll-top-btn");

  let ticking = false;

  window.addEventListener(
    "scroll",
    () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const scrollY = window.scrollY;

          // 헤더 배경 블러/색상 전환 (60px 이상)
          if (header) {
            header.classList.toggle("scrolled", scrollY > 60);
          }

          // 스크롤 탑 버튼 가시성 (300px 이상)
          if (scrollTopBtn) {
            scrollTopBtn.classList.toggle("visible", scrollY > 300);
          }

          ticking = false;
        });
        ticking = true;
      }
    },
    { passive: true },
  );

  // 스크롤 탑 버튼 클릭 시 부드럽게 상단 이동
  scrollTopBtn?.addEventListener("click", () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  });
}

/**
 * Intersection Observer (섹션 스크롤 진입 애니메이션 & 메뉴 스파이)
 * - threshold: 0.2 이상 권장 (0.25 적용)
 */
export function initIntersectionObserver() {
  const sections = document.querySelectorAll(".reveal");
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
