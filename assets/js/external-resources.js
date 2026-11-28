(function () {
  "use strict";
  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function render(root, data) {
    var style = el("style");
    style.textContent = ".kcore-resources{margin:28px 0;color:#eaf4fb}.kcore-resources h2{color:#f4fbff;margin:0 0 8px}.kcore-resources .kr-lead{color:#bdced9;line-height:1.6;max-width:900px}.kcore-resources .kr-group{margin:24px 0}.kcore-resources .kr-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:14px}.kcore-resources .kr-card{background:linear-gradient(145deg,#132638,#1b3040);border:1px solid rgba(127,174,197,.25);border-radius:15px;padding:16px;min-width:0}.kcore-resources .kr-card h3{font-size:1rem;color:#f4fbff;margin:5px 0 8px}.kcore-resources .kr-kind{font-size:.68rem;letter-spacing:.08em;color:#8dc8dc;text-transform:uppercase}.kcore-resources .kr-status{display:inline-block;margin:7px 0;padding:5px 8px;border:1px solid rgba(241,190,103,.35);border-radius:999px;color:#f2d49b;font-size:.7rem}.kcore-resources .kr-card p{color:#bdced9;font-size:.84rem;line-height:1.5;margin:5px 0 12px}.kcore-resources .kr-card a{display:inline-block;color:#a9e3ef;border:1px solid rgba(142,216,232,.4);border-radius:999px;padding:8px 12px;text-decoration:none}.kcore-resources .kr-card a:hover{background:rgba(142,216,232,.12)}.kcore-resources .kr-warning{border-left:3px solid #78c8d8;background:rgba(91,167,188,.09);padding:12px 15px;color:#d4e4ec;line-height:1.55;margin:18px 0}";
  root.appendChild(style);
  var wrap = el("div", "kcore-resources");
  wrap.appendChild(el("h2", "", data.title || "Семейные внешние ресурсы"));
  wrap.appendChild(el("p", "kr-lead", "Одинаковый каталог ссылок используется локальной и онлайн-версиями KOMAROVA_CORE. Каждая ссылка остаётся в своей категории и открывает указанный пользователем адрес."));
  (data.groups || []).forEach(function (group) {
    var section = el("section", "kr-group");
    section.appendChild(el("h3", "", group.title));
    var grid = el("div", "kr-grid");
    (group.items || []).forEach(function (item) {
      var card = el("article", "kr-card");
      card.appendChild(el("span", "kr-kind", item.category || ""));
      card.appendChild(el("h3", "", item.name || ""));
      card.appendChild(el("span", "kr-status", item.status || "Ссылка сохранена"));
      card.appendChild(el("p", "", item.note || ""));
      var link = el("a", "", "Открыть ресурс ↗");
      link.href = item.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.setAttribute("aria-label", "Открыть " + (item.name || "внешний ресурс") + " в новой вкладке");
      card.appendChild(link);
      grid.appendChild(card);
    });
    section.appendChild(grid);
    wrap.appendChild(section);
  });
  wrap.appendChild(el("p", "kr-warning", "Важно: наличие ссылки не означает, что сервис подключён к API, что файлы автоматически копируются или что выполнена двусторонняя синхронизация. Для этого нужны отдельная авторизация, серверный адаптер и проверка записи с обратным чтением. Пароли и токены в этом каталоге не хранятся."));
  root.appendChild(wrap);
  var source = root.getAttribute("data-resources-url");
  if (!source) {
    root.appendChild(el("p", "kr-warning", "Не задан адрес общего файла каталога."));
    return;
  }
  fetch(source, { credentials: "same-origin", cache: "no-cache" })
    .then(function (response) {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    })
    .then(function (data) { render(root, data); })
    .catch(function (error) {
      root.appendChild(el("p", "kr-warning", "Не удалось загрузить общий каталог ссылок: " + error.message));
    });
})();