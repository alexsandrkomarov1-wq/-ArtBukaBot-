(() => {
  "use strict";

  const start = Date.parse("2026-11-23T02:42:00Z");
  const loggedActiveSeconds = 68;
  const ageNode = document.querySelector("[data-project-age]");
  const workNode = document.querySelector("[data-project-worked]");
  const stampNode = document.querySelector("[data-project-start]");
  if (!ageNode || !workNode) return;

  const pad = value => String(value).padStart(2, "0");
  const format = total => {
    const seconds = Math.max(0, Math.floor(total));
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const rest = seconds % 60;
    return days + " д " + pad(hours) + ":" + pad(minutes) + ":" + pad(rest);
  };

  const update = () => {
    ageNode.textContent = format((Date.now() - start) / 1000);
    ageNode.dateTime = new Date(start).toISOString();
    const hours = Math.floor(loggedActiveSeconds / 3600);
    const minutes = Math.floor((loggedActiveSeconds % 3600) / 60);
    const seconds = loggedActiveSeconds % 60;
    workNode.textContent = pad(hours) + ":" + pad(minutes) + ":" + pad(seconds);
    if (stampNode) stampNode.textContent = new Intl.DateTimeFormat("ru-RU", {
      day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit",
      timeZone: "Europe/Amsterdam"
    }).format(new Date(start));
  };

  update();
  window.setInterval(update, 1000);
})();