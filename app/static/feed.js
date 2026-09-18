import { state, element, requestJson, makeLink } from "./core.js";
import { renderPost, renderComposer } from "./posts.js";

function feedKind() {
  return ({ "/following": "following", "/mine": "mine", "/saved": "saved" })[location.pathname] || "all";
}

function renderPagination(current, total) {
  const box = document.getElementById("pagination");
  box.replaceChildren();
  if (total < 2) return;
  const link = (number, label) => {
    const url = new URL(location.href);
    url.searchParams.set("page", number);
    return makeLink(url.pathname + url.search, label, "button button-outline small");
  };
  if (current > 1) box.append(link(current - 1, "← Назад"));
  box.append(element("span", "page-number", `${current} / ${total}`));
  if (current < total) box.append(link(current + 1, "Дальше →"));
}

export async function renderFeed() {
  const feed = document.getElementById("feed");
  feed.replaceChildren(element("div", "loading", "Загружаем заметки…"));
  const params = new URLSearchParams(location.search);
  params.set("feed", feedKind());
  if (state.profileUsername) params.set("author", state.profileUsername);
  try {
    const data = await requestJson(`/api/posts?${params.toString()}`);
    feed.replaceChildren();
    document.getElementById("feed-count").textContent = `${data.total} записей`;
    if (data.posts.length === 0) {
      feed.append(element("div", "empty-state panel", "Пока здесь тихо. Попробуйте другой запрос или создайте первую заметку."));
    } else {
      data.posts.forEach((post) => feed.append(renderPost(post, renderFeed)));
    }
    renderPagination(data.page, data.pages);
  } catch (error) {
    feed.replaceChildren(element("div", "empty-state panel", error.message));
  }
}

export async function renderTags() {
  const list = document.getElementById("tag-list");
  try {
    const data = await requestJson("/api/tags");
    list.replaceChildren();
    if (!data.tags.length) list.append(element("span", "muted", "Темы появятся вместе с заметками."));
    data.tags.forEach((tag) => list.append(makeLink(`/?tag=${encodeURIComponent(tag.name)}`, `#${tag.name}  ${tag.posts}`, "tag-pill")));
  } catch (error) {
    list.textContent = "Не удалось загрузить темы.";
  }
}

function renderSearch() {
  const params = new URLSearchParams(location.search);
  document.getElementById("search-input").value = params.get("q") || "";
  document.getElementById("search-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const value = document.getElementById("search-input").value.trim();
    const url = new URL(location.href);
    if (value) url.searchParams.set("q", value);
    else url.searchParams.delete("q");
    url.searchParams.delete("page");
    location.href = url.pathname + url.search;
  });
  if (params.has("tag")) {
    const filter = document.getElementById("active-filter");
    filter.hidden = false;
    const url = new URL(location.href);
    url.searchParams.delete("tag");
    filter.append(element("span", "", `Тема: #${params.get("tag")}`), makeLink(url.pathname + url.search, "Сбросить ×"));
  }
}

export function configureFeedPage() {
  document.getElementById("feed-section").hidden = false;
  const kind = feedKind();
  const labels = { all: "Общая лента", following: "Лента подписок", mine: "Мои заметки", saved: "Сохранённое" };
  document.getElementById("feed-heading").textContent = state.profileUsername ? `Заметки @${state.profileUsername}` : labels[kind];
  if (kind !== "all") {
    document.getElementById("page-title").textContent = labels[kind];
    document.getElementById("page-description").textContent = kind === "following" ? "Свежие мысли людей, на которых вы подписаны." : kind === "saved" ? "Заметки, к которым хочется вернуться." : "Все ваши идеи в одном месте.";
  }
  renderSearch();
  renderComposer(renderFeed);
  renderFeed();
}

