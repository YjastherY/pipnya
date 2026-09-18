export const state = { page: document.body.dataset.page, profileUsername: document.body.dataset.profileUsername, viewer: null };
const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

export function element(tag, className = "", value = "") {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (value) node.textContent = value;
  return node;
}

export async function requestJson(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.method && options.method !== "GET" ? { "X-CSRF-Token": csrfToken } : {}),
      ...options.headers,
    },
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "Не удалось выполнить запрос");
  return result;
}

export function showError(target, message) {
  target.textContent = message;
  target.hidden = !message;
}

export function makeLink(href, label, className = "") {
  const link = element("a", className, label);
  link.href = href;
  return link;
}

export function makeButton(label, className = "") {
  const button = element("button", className, label);
  button.type = "button";
  return button;
}

export function formatDate(value) {
  return new Intl.DateTimeFormat("ru-RU", { day: "numeric", month: "long", year: "numeric" }).format(new Date(value));
}

export function avatarLetter(name) {
  return name.slice(0, 1).toUpperCase();
}

export function renderNavigation() {
  const account = document.getElementById("account-nav");
  account.replaceChildren();
  if (state.viewer) {
    account.append(makeLink(`/profile/${encodeURIComponent(state.viewer.username)}`, `@${state.viewer.username}`, "account-link"));
    const logout = makeButton("Выйти", "button button-outline small");
    logout.addEventListener("click", async () => {
      await requestJson("/api/logout", { method: "POST" });
      location.href = "/";
    });
    account.append(logout);
    document.getElementById("join-link").hidden = true;
  } else {
    account.append(makeLink("/login", "Войти", "account-link"));
    account.append(makeLink("/register", "Создать аккаунт", "button button-primary small"));
  }
  const active = location.pathname === "/following" ? "following" : location.pathname === "/saved" ? "saved" : "all";
  document.querySelectorAll("[data-nav]").forEach((link) => {
    if (link.dataset.nav === active) link.setAttribute("aria-current", "page");
  });
}
