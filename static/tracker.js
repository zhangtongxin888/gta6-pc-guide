/* Filter, sort, and the console-launch clock. No network calls. */
(function () {
  function pad(n) {
    return (n < 10 ? "0" : "") + n;
  }

  function tick() {
    var nodes = document.querySelectorAll("[data-since]");
    if (!nodes.length) return;
    var start = Date.parse(nodes[0].getAttribute("data-since"));
    if (!isFinite(start)) return;
    function render() {
      var diff = Math.max(0, Date.now() - start);
      var s = Math.floor(diff / 1000);
      var days = Math.floor(s / 86400);
      var hours = Math.floor((s % 86400) / 3600);
      var mins = Math.floor((s % 3600) / 60);
      var secs = s % 60;
      nodes.forEach(function (n) {
        var map = { d: String(days), h: pad(hours), m: pad(mins), s: pad(secs) };
        Object.keys(map).forEach(function (k) {
          var el = n.querySelector('[data-u="' + k + '"]');
          if (el) el.textContent = map[k];
        });
      });
    }
    render();
    setInterval(render, 1000);
  }

  function race() {
    var root = document.querySelector("[data-race]");
    if (!root) return;
    var cards = Array.prototype.slice.call(root.querySelectorAll("[data-card]"));
    var chips = document.querySelectorAll("[data-filter]");
    var sort = document.querySelector("[data-sort]");
    var q = document.querySelector("[data-q]");
    var count = document.querySelector("[data-count]");
    var filter = "all";

    function apply() {
      var query = (q && q.value || "").trim().toLowerCase();
      var mode = sort ? sort.value : "score";
      var list = cards.slice().sort(function (a, b) {
        var ds = (+b.dataset.score || 0) - (+a.dataset.score || 0);
        var dt = (+b.dataset.stage || 0) - (+a.dataset.stage || 0);
        if (mode === "stage") return dt || ds;
        if (mode === "updated") return (b.dataset.updated || "").localeCompare(a.dataset.updated || "") || ds;
        return ds || dt;
      });
      var n = 0;
      list.forEach(function (card) {
        var gpu = (card.dataset.gpu || "").toLowerCase().split(/\s+/);
        var halted = card.dataset.halted === "1";
        var ok = true;
        if (filter === "halted") ok = halted;
        else if (filter !== "all") ok = gpu.indexOf(filter) !== -1;
        var text = (card.dataset.search || "").toLowerCase();
        if (query && text.indexOf(query) === -1) ok = false;
        card.hidden = !ok;
        if (ok) n++;
        root.appendChild(card);
      });
      if (count) {
        var tmpl = count.getAttribute("data-template") || "";
        count.textContent = tmpl.replace("%%n", String(n)).replace("%%t", String(cards.length));
      }
    }

    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        filter = chip.getAttribute("data-filter") || "all";
        chips.forEach(function (c) { c.setAttribute("aria-pressed", c === chip ? "true" : "false"); });
        apply();
      });
    });
    if (sort) sort.addEventListener("change", apply);
    if (q) q.addEventListener("input", apply);
    apply();
  }

  function news() {
    var root = document.querySelector("[data-news]");
    if (!root) return;
    var cards = root.querySelectorAll("[data-tag]");
    var chips = document.querySelectorAll("[data-news-filter]");
    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        var f = chip.getAttribute("data-news-filter") || "all";
        chips.forEach(function (c) { c.setAttribute("aria-pressed", c === chip ? "true" : "false"); });
        cards.forEach(function (card) {
          card.hidden = f !== "all" && card.getAttribute("data-tag") !== f;
        });
      });
    });
  }

  tick();
  race();
  news();
})();
