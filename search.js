(function () {
  "use strict";

  var input = document.getElementById("site-search");
  var resultsEl = document.getElementById("search-results");
  if (!input || !resultsEl) return;

  var BOOK_FILE = { 1: "boek1.html", 2: "boek2.html", 3: "boek3.html", 4: "boek4.html" };
  var index = null;
  var indexPromise = null;
  var activeIndex = -1;
  var currentItems = [];
  var debounceTimer = null;

  function normalize(s) {
    return (s || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[̀-ͯ]/g, ""); // strip diacritics (é -> e, etc.)
  }

  function loadIndex() {
    if (indexPromise) return indexPromise;
    indexPromise = fetch("search-index.json")
      .then(function (r) { return r.json(); })
      .then(function (data) {
        index = data.map(function (e) {
          return {
            raw: e,
            nt: normalize(e.t),
            nx: normalize(e.x),
          };
        });
        return index;
      })
      .catch(function () {
        index = [];
        return index;
      });
    return indexPromise;
  }

  function score(entry, q, qWords) {
    var s = 0;
    if (entry.nt.indexOf(q) === 0) s += 100;
    else if (entry.nt.indexOf(q) !== -1) s += 60;
    qWords.forEach(function (w) {
      if (w.length < 2) return;
      if (entry.nt.indexOf(w) !== -1) s += 12;
      if (entry.nx.indexOf(w) !== -1) s += 3;
    });
    if (entry.nx.indexOf(q) !== -1) s += 20;
    // shorter / higher-level titles (hoofdstukken/delen) rank slightly higher on ties
    if (entry.raw.lv === "deel") s += 2;
    if (entry.raw.lv === "chap") s += 1;
    return s;
  }

  function snippetAround(text, q) {
    if (!text) return "";
    var nt = normalize(text);
    var i = nt.indexOf(q);
    if (i === -1) return text.slice(0, 140) + (text.length > 140 ? "…" : "");
    var start = Math.max(0, i - 50);
    var end = Math.min(text.length, i + q.length + 90);
    var snippet = (start > 0 ? "…" : "") + text.slice(start, end) + (end < text.length ? "…" : "");
    return snippet;
  }

  function highlight(snippet, q) {
    if (!q) return escapeHtml(snippet);
    var nSnippet = normalize(snippet);
    var out = "";
    var pos = 0;
    var i;
    while ((i = nSnippet.indexOf(q, pos)) !== -1) {
      out += escapeHtml(snippet.slice(pos, i));
      out += "<mark>" + escapeHtml(snippet.slice(i, i + q.length)) + "</mark>";
      pos = i + q.length;
    }
    out += escapeHtml(snippet.slice(pos));
    return out;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
  }

  function render(items, q) {
    currentItems = items;
    activeIndex = -1;
    if (!q) {
      resultsEl.hidden = true;
      resultsEl.innerHTML = "";
      return;
    }
    if (!items.length) {
      resultsEl.innerHTML = '<p class="sr-empty">Niets gevonden voor “' + escapeHtml(q) + '”.</p>';
      resultsEl.hidden = false;
      return;
    }
    var html = items.map(function (it, i) {
      var e = it.raw;
      var snippet = snippetAround(e.x, normalize(q));
      return (
        '<a class="sr-item" data-idx="' + i + '" href="' + BOOK_FILE[e.b] + "#" + e.a + '">' +
        '<div class="sr-book">Boek ' + e.b + " — " + escapeHtml(e.bt) + "</div>" +
        '<div class="sr-title">' + highlight(e.t, normalize(q)) + "</div>" +
        (snippet ? '<div class="sr-snippet">' + highlight(snippet, normalize(q)) + "</div>" : "") +
        "</a>"
      );
    }).join("");
    resultsEl.innerHTML = html;
    resultsEl.hidden = false;
  }

  function search(q) {
    var nq = normalize(q.trim());
    if (!nq) { render([], ""); return; }
    loadIndex().then(function (idx) {
      var qWords = nq.split(/\s+/);
      var scored = idx
        .map(function (entry) { return { raw: entry.raw, s: score(entry, nq, qWords) }; })
        .filter(function (r) { return r.s > 0; })
        .sort(function (a, b) { return b.s - a.s; })
        .slice(0, 20);
      render(scored, q.trim());
    });
  }

  input.addEventListener("input", function () {
    clearTimeout(debounceTimer);
    var q = input.value;
    debounceTimer = setTimeout(function () { search(q); }, 150);
  });
  input.addEventListener("focus", function () { loadIndex(); });

  input.addEventListener("keydown", function (e) {
    var items = resultsEl.querySelectorAll(".sr-item");
    if (e.key === "Escape") {
      render([], "");
      input.blur();
    } else if (e.key === "ArrowDown" && items.length) {
      e.preventDefault();
      activeIndex = Math.min(activeIndex + 1, items.length - 1);
      updateActive(items);
    } else if (e.key === "ArrowUp" && items.length) {
      e.preventDefault();
      activeIndex = Math.max(activeIndex - 1, 0);
      updateActive(items);
    } else if (e.key === "Enter" && items.length) {
      e.preventDefault();
      var target = activeIndex >= 0 ? items[activeIndex] : items[0];
      window.location.href = target.getAttribute("href");
    }
  });

  function updateActive(items) {
    items.forEach(function (el, i) { el.classList.toggle("is-active", i === activeIndex); });
    if (activeIndex >= 0) items[activeIndex].scrollIntoView({ block: "nearest" });
  }

  document.addEventListener("click", function (e) {
    if (!e.target.closest(".header-search")) {
      resultsEl.hidden = true;
    }
  });

  // Ondersteunt ?q=... in de URL (bijv. vanuit de SearchAction in de
  // structured data, of een gedeelde link) door de zoekbalk meteen te vullen
  // en te doorzoeken.
  try {
    var qParam = new URLSearchParams(window.location.search).get("q");
    if (qParam) {
      input.value = qParam;
      search(qParam);
      input.focus();
    }
  } catch (e) { /* URLSearchParams niet beschikbaar: geen probleem, gewoon negeren */ }
})();
