(() => {
  "use strict";
  document.addEventListener("click", (event) => {
    const trigger = event.target.closest("[data-world-open-guide]");
    if (!trigger) return;
    const toggle = document.querySelector("[data-guide-toggle]");
    const panel = document.querySelector("[data-guide-panel]");
    if (!toggle || !panel) {
      window.location.hash = "site-guide";
      return;
    }
    if (panel.hidden) toggle.click();
    panel.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "nearest" });
  });
})();