(function () {
  "use strict";
  document.documentElement.classList.remove("no-js");
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Header shadow on scroll */
  const header = document.querySelector(".header");
  const onScroll = () => header && header.classList.toggle("is-scrolled", window.scrollY > 8);
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* Mobile nav */
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("site-nav");
  if (toggle && nav) {
    const setOpen = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
      toggle.querySelector("use").setAttribute("href", open ? "#i-close" : "#i-menu");
      if (open) nav.style.setProperty("--nav-h", window.innerHeight - header.getBoundingClientRect().bottom + "px");
      nav.classList.toggle("is-open", open);
      document.body.classList.toggle("nav-open", open);
    };
    toggle.addEventListener("click", () => setOpen(toggle.getAttribute("aria-expanded") !== "true"));
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && nav.classList.contains("is-open")) { setOpen(false); toggle.focus(); }
    });
    window.matchMedia("(min-width: 1025px)").addEventListener("change", (e) => e.matches && setOpen(false));
  }

  /* Solutions submenu (click/keyboard; hover handled in CSS on desktop) */
  document.querySelectorAll(".nav__item--has-menu").forEach((item) => {
    const btn = item.querySelector("button");
    const set = (open) => { item.dataset.open = String(open); btn.setAttribute("aria-expanded", String(open)); };
    btn.addEventListener("click", () => set(item.dataset.open !== "true"));
    item.addEventListener("keydown", (e) => { if (e.key === "Escape") { set(false); btn.focus(); } });
    document.addEventListener("click", (e) => { if (!item.contains(e.target)) set(false); });
  });

  /* Reveal on scroll */
  const reveals = document.querySelectorAll(".reveal");
  if (!reduceMotion && "IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) { entry.target.classList.add("is-visible"); io.unobserve(entry.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach((el) => { el.style.transitionDelay = (el.dataset.delay || 0) + "ms"; io.observe(el); });
  } else {
    reveals.forEach((el) => el.classList.add("is-visible"));
  }

  /* Industries explorer: ARIA tabs with deep links (#oil-gas etc.) */
  const tablist = document.querySelector("[role='tablist']");
  if (tablist) {
    const tabs = Array.from(tablist.querySelectorAll("[role='tab']"));
    const select = (tab, { focus = false, push = true } = {}) => {
      tabs.forEach((t) => {
        const selected = t === tab;
        t.setAttribute("aria-selected", String(selected));
        t.tabIndex = selected ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !selected;
      });
      if (focus) tab.focus();
      tab.scrollIntoView({ block: "nearest", inline: "nearest", behavior: reduceMotion ? "auto" : "smooth" });
      if (push) history.replaceState(null, "", "#" + tab.dataset.slug);
    };
    tabs.forEach((tab, i) => {
      tab.addEventListener("click", () => select(tab));
      tab.addEventListener("keydown", (e) => {
        const keys = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 };
        if (e.key in keys) { e.preventDefault(); select(tabs[(i + keys[e.key] + tabs.length) % tabs.length], { focus: true }); }
        if (e.key === "Home") { e.preventDefault(); select(tabs[0], { focus: true }); }
        if (e.key === "End") { e.preventDefault(); select(tabs[tabs.length - 1], { focus: true }); }
      });
    });
    const fromHash = () => {
      const slug = location.hash.slice(1);
      const tab = tabs.find((t) => t.dataset.slug === slug);
      select(tab || tabs[0], { push: false });
    };
    window.addEventListener("hashchange", fromHash);
    fromHash();
  }

  /* Contact form: prefill topic from ?topic= and validate inline */
  const form = document.querySelector("#enquiry-form");
  if (form) {
    const topic = new URLSearchParams(location.search).get("topic");
    const topicSelect = form.querySelector("#topic");
    if (topic && topicSelect && topicSelect.querySelector(`option[value="${CSS.escape(topic)}"]`)) topicSelect.value = topic;

    const validate = (input) => {
      const field = input.closest(".field");
      const ok = input.checkValidity();
      field.classList.toggle("is-invalid", !ok);
      input.setAttribute("aria-invalid", String(!ok));
      return ok;
    };
    form.querySelectorAll("input, select, textarea").forEach((input) => {
      input.addEventListener("blur", () => validate(input));
      input.addEventListener("input", () => input.closest(".field").classList.contains("is-invalid") && validate(input));
    });
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const inputs = Array.from(form.querySelectorAll("[required]"));
      const invalid = inputs.filter((input) => !validate(input));
      if (invalid.length) { invalid[0].focus(); return; }
      const btn = form.querySelector("button[type='submit']");
      btn.disabled = true;
      btn.textContent = "Sending…";
      // TODO: connect to a form backend (e.g. Formspree, HubSpot or your CRM endpoint).
      setTimeout(() => {
        form.reset();
        btn.disabled = false;
        btn.textContent = "Send enquiry";
        const status = form.querySelector(".form__status");
        status.classList.add("is-visible");
        status.focus();
      }, 700);
    });
  }

  /* Client marquee: duplicate items for a seamless loop, with a pause control */
  document.querySelectorAll("[data-marquee]").forEach((marquee) => {
    const track = marquee.querySelector(".marquee__track");
    Array.from(track.children).forEach((item) => {
      const clone = item.cloneNode(true);
      clone.setAttribute("aria-hidden", "true");
      track.appendChild(clone);
    });
    const toggle = marquee.closest("section").querySelector(".marquee-toggle");
    if (toggle) {
      toggle.addEventListener("click", () => {
        const paused = marquee.classList.toggle("is-paused");
        toggle.setAttribute("aria-pressed", String(paused));
        toggle.querySelector("span").textContent = paused ? "Play" : "Pause";
      });
    }
  });

  /* Footer year */
  document.querySelectorAll("[data-year]").forEach((el) => (el.textContent = new Date().getFullYear()));
})();
