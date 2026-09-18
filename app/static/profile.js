import { state, element, requestJson, makeButton, formatDate, avatarLetter } from "./core.js";

export async function renderProfile() {
  const panel = document.getElementById("profile-panel");
  panel.hidden = false;
  try {
    const result = await requestJson(`/api/users/${encodeURIComponent(state.profileUsername)}`);
    const user = result.user;
    document.getElementById("page-title").textContent = `@${user.username}`;
    document.getElementById("page-description").textContent = "Заметки, которыми делится этот автор.";
    const head = element("div", "profile-head");
    head.append(element("span", "avatar profile-avatar", avatarLetter(user.username)));
    const info = element("div");
    info.append(element("span", "kicker", "УЧАСТНИК МАЯКА"), element("h2", "", `@${user.username}`), element("p", "muted", `С нами с ${formatDate(user.created_at)}`));
    head.append(info);
    panel.append(head);
    const stats = element("div", "profile-stats");
    [[user.posts, "заметок"], [user.followers, "подписчиков"], [user.following, "подписок"]].forEach(([number, label]) => {
      const stat = element("div");
      stat.append(element("strong", "", String(number)), element("span", "", label));
      stats.append(stat);
    });
    panel.append(stats);
    if (state.viewer && state.viewer.id !== user.id) {
      const follow = makeButton(user.is_following ? "Отписаться" : "Подписаться", user.is_following ? "button button-outline" : "button button-primary");
      follow.addEventListener("click", async () => {
        follow.disabled = true;
        try {
          await requestJson(`/api/users/${encodeURIComponent(user.username)}/follow`, { method: user.is_following ? "DELETE" : "POST" });
          panel.replaceChildren();
          await renderProfile();
        } catch (error) {
          alert(error.message);
          follow.disabled = false;
        }
      });
      panel.append(follow);
    }
  } catch (error) {
    panel.append(element("p", "form-error", error.message));
  }
}

