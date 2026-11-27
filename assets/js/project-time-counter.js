(() => {
  "use strict";

  const counter = document.querySelector("[data-project-time-counter]");
  if (!counter) return;

  // Единственная конфигурация счётчиков находится в _data/project_time.yml.
  const start = Date.parse(counter.dataset.projectStartUtc || "");
  const loggedActiveSeconds = Number.parseInt(counter.dataset.projectWorkedSeconds || "", 10);
  const timezone = counter.dataset.projectTimezone || "Europe/Amsterdam";
  const ageNode = counter.querySelector("[data-project-age]");
  const workNode = counter.querySelector("[data-project-worked]");
  const stampNode = counter.querySelector("[data-project-start]");

  if (!Number.isFinite(start) || !Number.isFinite(loggedActiveSeconds) ||
      loggedActiveSeconds < 0 || !ageNode || !workNode) return;

  const pad = value => String(value).padStart(2, "0");
  const formatAge = total => {
    const seconds = Math.max(0, Math.floor(total));
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const rest = seconds % 60;
    return days + " д " + pad(hours) + ":" + pad(minutes) + ":" + pad(rest);
  };

  const update = () => {
    ageNode.textContent = formatAge((Date.now() - start) / 1000);
    ageNode.dateTime = new Date(start).toISOString();

    const hours = Math.floor(loggedActiveSeconds / 3600);
    const minutes = Math.floor((loggedActiveSeconds % 3600) / 60);
    const seconds = loggedActiveSeconds % 60;
    workNode.textContent = pad(hours) + ":" + pad(minutes) + ":" + pad(seconds);

    if (stampNode) {
      stampNode.textContent = new Intl.DateTimeFormat("ru-RU", {
        day: "numeric",
        month: "long",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        timeZone: timezone
      }).format(new Date(start));
      stampNode.dateTime = new Date(start).toISOString();
    }
  };

  update();
  window.setInterval(update, 1000);
})();