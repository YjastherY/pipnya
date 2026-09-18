import { state, element, requestJson, showError, makeLink, makeButton, formatDate, avatarLetter } from "./core.js";

function tagsFromInput(value) {
  return value.split(",").map((tag) => tag.trim()).filter(Boolean);
}

export function renderComposer(onChanged) {
  if (!state.viewer || !["/", "/mine"].includes(location.pathname)) return;
  const composer = document.getElementById("composer");
  composer.hidden = false;
  document.getElementById("composer-avatar").textContent = avatarLetter(state.viewer.username);
  const textarea = document.getElementById("post-body");
  textarea.addEventListener("input", () => {
    document.getElementById("character-count").textContent = `${textarea.value.length} / 1000`;
  });
  document.getElementById("composer-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const submit = form.querySelector('button[type="submit"]');
    submit.disabled = true;
    showError(document.getElementById("composer-error"), "");
    try {
      await requestJson("/api/posts", {
        method: "POST",
        body: JSON.stringify({ body: textarea.value, tags: tagsFromInput(document.getElementById("post-tags").value) }),
      });
      form.reset();
      document.getElementById("character-count").textContent = "0 / 1000";
      if (location.search) location.href = location.pathname;
      else await onChanged();
    } catch (error) {
      showError(document.getElementById("composer-error"), error.message);
    } finally {
      submit.disabled = false;
    }
  });
}

export function renderPost(post, onChanged) {
  const card = element("article", "post-card panel");
  const head = element("div", "post-head");
  const avatar = makeLink(`/profile/${encodeURIComponent(post.username)}`, avatarLetter(post.username), "avatar");
  const byline = element("div", "post-byline");
  byline.append(makeLink(`/profile/${encodeURIComponent(post.username)}`, `@${post.username}`, "post-author"));
  const time = element("time", "post-date", formatDate(post.created_at));
  time.dateTime = post.created_at;
  byline.append(time);
  head.append(avatar, byline);
  if (post.updated_at) head.append(element("span", "edited-label", "изменено"));
  card.append(head);
  const body = element("p", "post-body", post.body);
  card.append(body);
  const tags = element("div", "post-tags");
  post.tags.forEach((tag) => {
    tags.append(makeLink(`/?tag=${encodeURIComponent(tag)}`, `#${tag}`, "tag-link"));
  });
  card.append(tags);
  const actions = element("div", "post-actions");
  const bookmark = makeButton(post.bookmarked ? "◆ Сохранено" : "◇ Сохранить", "post-action");
  bookmark.setAttribute("aria-label", post.bookmarked ? "Убрать из сохранённого" : "Сохранить заметку");
  bookmark.addEventListener("click", async () => {
    if (!state.viewer) {
      location.href = "/login";
      return;
    }
    bookmark.disabled = true;
    try {
      await requestJson(`/api/posts/${post.id}/bookmark`, { method: post.bookmarked ? "DELETE" : "POST" });
      await onChanged();
    } catch (error) {
      alert(error.message);
      bookmark.disabled = false;
    }
  });
  actions.append(bookmark);
  if (state.viewer && state.viewer.id === post.author_id) {
    const edit = makeButton("Изменить", "post-action");
    edit.addEventListener("click", () => renderPostEditor(card, post, onChanged));
    const remove = makeButton("Удалить", "post-action danger");
    remove.addEventListener("click", async () => {
      if (!confirm("Удалить эту заметку?")) return;
      try {
        await requestJson(`/api/posts/${post.id}`, { method: "DELETE" });
        await onChanged();
      } catch (error) {
        alert(error.message);
      }
    });
    actions.append(edit, remove);
  }
  card.append(actions);
  return card;
}

function renderPostEditor(card, post, onChanged) {
  if (card.querySelector(".edit-form")) return;
  const form = element("form", "edit-form");
  const textarea = element("textarea", "edit-textarea");
  textarea.maxLength = 1000;
  textarea.value = post.body;
  const tags = element("input", "edit-tags");
  tags.placeholder = "Теги через запятую";
  tags.value = post.tags.join(", ");
  const row = element("div", "edit-controls");
  const cancel = makeButton("Отмена", "button button-outline small");
  cancel.addEventListener("click", () => {
    form.replaceWith(element("p", "post-body", post.body));
    card.querySelector(".post-tags").hidden = false;
    card.querySelector(".post-actions").hidden = false;
  });
  const save = element("button", "button button-primary small", "Сохранить");
  save.type = "submit";
  row.append(cancel, save);
  const errorBox = element("p", "form-error");
  errorBox.hidden = true;
  form.append(textarea, tags, errorBox, row);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    save.disabled = true;
    try {
      await requestJson(`/api/posts/${post.id}`, {
        method: "PATCH",
        body: JSON.stringify({ body: textarea.value, tags: tagsFromInput(tags.value) }),
      });
      await onChanged();
    } catch (error) {
      showError(errorBox, error.message);
      save.disabled = false;
    }
  });
  card.querySelector(".post-body").replaceWith(form);
  card.querySelector(".post-tags").hidden = true;
  card.querySelector(".post-actions").hidden = true;
  textarea.focus();
}
