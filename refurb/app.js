(function () {
  "use strict";

  /* Mobile menu */
  const menuBtn = document.querySelector(".menu-btn");
  const nav = document.getElementById("nav");
  menuBtn.addEventListener("click", () => {
    const open = menuBtn.getAttribute("aria-expanded") !== "true";
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    nav.classList.toggle("is-open", open);
  });
  nav.addEventListener("click", (e) => {
    if (e.target.closest("a")) { menuBtn.setAttribute("aria-expanded", "false"); nav.classList.remove("is-open"); }
  });

  /* Filter by need + search by model */
  const cards = Array.from(document.querySelectorAll("[data-grid] .card"));
  const needs = Array.from(document.querySelectorAll(".need"));
  const empty = document.querySelector("[data-empty]");
  const search = document.getElementById("q");
  let need = "all";

  const apply = () => {
    const q = search.value.trim().toLowerCase();
    let shown = 0;
    cards.forEach((card) => {
      const matchNeed = need === "all" || card.dataset.needs.split(" ").includes(need);
      const matchText = !q || card.textContent.toLowerCase().includes(q);
      card.hidden = !(matchNeed && matchText);
      if (!card.hidden) shown++;
    });
    empty.hidden = shown > 0;
  };
  const setNeed = (value) => {
    need = value;
    needs.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.need === value)));
    apply();
  };
  needs.forEach((b) => b.addEventListener("click", () => setNeed(b.dataset.need)));
  document.querySelector("[data-reset]").addEventListener("click", () => { search.value = ""; setNeed("all"); });
  search.addEventListener("input", apply);
  search.form.addEventListener("submit", (e) => { e.preventDefault(); apply(); document.getElementById("shop").scrollIntoView(); });

  /* Add to cart: the button confirms, the cart count updates, a toast names the item */
  const countEl = document.querySelector("[data-cart-count]");
  const cartLink = document.querySelector(".cart");
  const toast = document.querySelector("[data-toast]");
  let count = 0;
  let toastTimer;
  document.querySelectorAll("[data-add]").forEach((btn) => {
    btn.addEventListener("click", () => {
      count++;
      countEl.textContent = count;
      cartLink.setAttribute("aria-label", `Cart, ${count} item${count === 1 ? "" : "s"}`);
      countEl.classList.add("bump");
      setTimeout(() => countEl.classList.remove("bump"), 250);
      btn.textContent = "Added to cart";
      btn.classList.add("is-added");
      setTimeout(() => { btn.textContent = "Add to cart"; btn.classList.remove("is-added"); }, 1800);
      toast.textContent = `Added ${btn.dataset.add} to your cart.`;
      toast.classList.add("is-on");
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => toast.classList.remove("is-on"), 2600);
    });
  });

  /* Trade-in estimate (placeholder pricing table) */
  const quote = document.querySelector("[data-quote]");
  const out = document.querySelector("[data-quote-out]");
  const base = { apple: 320, lenovo: 190, dell: 170, hp: 160, other: 110 };
  const ageFactor = [1, 0.72, 0.45, 0.25];
  const condFactor = { good: 1, worn: 0.6, broken: 0.2 };
  const round5 = (n) => Math.max(5, Math.round(n / 5) * 5);
  const update = () => {
    const f = new FormData(quote);
    const mid = base[f.get("brand")] * ageFactor[+f.get("age")] * condFactor[f.get("cond")];
    out.textContent = `$${round5(mid * 0.85)} – $${round5(mid * 1.15)}`;
  };
  quote.addEventListener("change", update);
  update();
})();
