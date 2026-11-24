(function () {
  const root = document.querySelector("[data-core-portal]");
  if (!root) return;

  const apiBase = (root.dataset.apiBase || "").trim().replace(/\/+$/, "");
  const notice = root.querySelector("[data-portal-notice]");
  const loginPanel = root.querySelector("[data-login-panel]");
  const privatePanel = root.querySelector("[data-private-panel]");
  const loginForm = root.querySelector("[data-login-form]");
  const personForm = root.querySelector("[data-person-form]");
  const peopleList = root.querySelector("[data-people-list]");
  const userName = root.querySelector("[data-user-name]");
  const userRole = root.querySelector("[data-user-role]");
  const tokenKey = "komarova_core_access_token";
  let token = sessionStorage.getItem(tokenKey) || "";

  function setNotice(message, kind) {
    notice.textContent = message;
    notice.dataset.kind = kind || "info";
  }

  async function request(path, options) {
    const config = options || {};
    const headers = new Headers(config.headers || {});
    if (token) headers.set("Authorization", "Bearer " + token);
    if (config.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
    const response = await fetch(apiBase + path, { ...config, headers });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = payload.detail;
      throw new Error(typeof detail === "string" ? detail : (detail && detail.message) || ("HTTP " + response.status));
    }
    return payload;
  }

  function showLogin() {
    loginPanel.hidden = false;
    privatePanel.hidden = true;
  }

  function showPrivate() {
    loginPanel.hidden = true;
    privatePanel.hidden = false;
  }

  function renderPeople(people) {
    peopleList.replaceChildren();
    if (!people.length) {
      const empty = document.createElement("li");
      empty.className = "portal-empty";
      empty.textContent = "В реестре пока нет записей.";
      peopleList.append(empty);
      return;
    }
    for (const person of people) {
      const item = document.createElement("li");
      const name = document.createElement("strong");
      name.textContent = person.display_name;
      const id = document.createElement("small");
      id.textContent = person.person_id;
      item.append(name, id);
      peopleList.append(item);
    }
  }

  async function loadPeople() {
    const people = await request("/api/v1/people?limit=100");
    renderPeople(people);
  }

  async function loadSession() {
    const user = await request("/api/v1/auth/me");
    userName.textContent = user.username;
    userRole.textContent = "Роль: " + user.role;
    showPrivate();
    await loadPeople();
    setNotice("Вход выполнен. Данные получены из семейного API.");
  }

  loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    if (!apiBase) return setNotice("Адрес API ещё не настроен. Публичный сайт не подключён к семейной базе.", "error");
    const button = loginForm.querySelector("button[type=submit]");
    button.disabled = true;
    try {
      const data = await request("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({
          username: loginForm.elements.username.value.trim(),
          password: loginForm.elements.password.value
        })
      });
      token = data.access_token;
      sessionStorage.setItem(tokenKey, token);
      loginForm.reset();
      await loadSession();
    } catch (error) {
      token = "";
      sessionStorage.removeItem(tokenKey);
      showLogin();
      setNotice(error.message || "Не удалось выполнить вход.", "error");
    } finally {
      button.disabled = false;
    }
  });

  personForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const button = personForm.querySelector("button[type=submit]");
    button.disabled = true;
    try {
      await request("/api/v1/people", {
        method: "POST",
        body: JSON.stringify({ display_name: personForm.elements.display_name.value })
      });
      personForm.reset();
      await loadPeople();
      setNotice("Запись добавлена в семейный реестр.");
    } catch (error) {
      setNotice(error.message || "Не удалось добавить запись.", "error");
    } finally {
      button.disabled = false;
    }
  });

  root.querySelector("[data-refresh]").addEventListener("click", async function () {
    try {
      await loadPeople();
      setNotice("Реестр обновлён.");
    } catch (error) {
      setNotice(error.message || "Не удалось обновить реестр.", "error");
    }
  });

  root.querySelector("[data-logout]").addEventListener("click", async function () {
    try { await request("/api/v1/auth/logout", { method: "POST" }); } catch (_) {}
    token = "";
    sessionStorage.removeItem(tokenKey);
    showLogin();
    renderPeople([]);
    setNotice("Сеанс завершён.");
  });

  if (!apiBase) {
    setNotice("Интерфейс готов, но адрес API ещё не задан. После развёртывания backend укажем HTTPS-адрес в конфигурации сайта.", "error");
    showLogin();
  } else if (token) {
    loadSession().catch(function (error) {
      token = "";
      sessionStorage.removeItem(tokenKey);
      showLogin();
      setNotice(error.message || "Сеанс недействителен. Войдите снова.", "error");
    });
  } else {
    setNotice("Введите данные учётной записи KOMAROVA_CORE.");
    showLogin();
  }
})();