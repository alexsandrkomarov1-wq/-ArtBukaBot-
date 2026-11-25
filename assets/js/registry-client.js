(() => {
  let base = "";
  let token = "";
  let currentUser = null;
  const networkMessage = () => "Частный backend не отвечает. Проверьте адрес API, HTTPS, CORS и факт развёртывания сервиса.";
  const normalizeBase = value => {
    const url = new URL(value.trim());
    if (url.protocol !== "https:" && !(url.hostname === "localhost" || url.hostname === "127.0.0.1")) {
      throw new Error("Для удалённого API требуется HTTPS.");
    }
    return url.href.replace(/\/$/, "");
  };
  async function request(path, options = {}) {
    if (!base || !token) throw new Error("Сначала подключитесь к API и войдите в семейный аккаунт.");
    let response;
    try {
      response = await fetch(base + path, {
      ...options,
      headers: {
        "Accept": "application/json",
        ...(options.body ? {"Content-Type":"application/json"} : {}),
        "Authorization": "Bearer " + token,
        ...(options.headers || {})
      }
      });
    } catch (error) {
      if (error instanceof TypeError) throw new Error(networkMessage());
      throw error;
    }
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = typeof payload.detail === "string" ? payload.detail : "HTTP " + response.status;
      throw new Error(detail);
    }
    return payload;
  }
  async function login(apiBase, username, password) {
    base = normalizeBase(apiBase);
    token = "";
    currentUser = null;
    let response;
    try {
      response = await fetch(base + "/api/v1/auth/login", {
      method:"POST",
      headers:{"Content-Type":"application/json","Accept":"application/json"},
      body:JSON.stringify({username,password})
      });
    } catch (error) {
      if (error instanceof TypeError) throw new Error(networkMessage());
      throw error;
    }
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.detail || "Не удалось войти. HTTP " + response.status);
    token = payload.access_token;
    currentUser = payload.user;
    return currentUser;
  }
  window.KomCoreRegistry = {
    login,
    request,
    get user(){ return currentUser; },
    disconnect(){ token=""; currentUser=null; }
  };
})();