import { state, element, requestJson, renderNavigation } from "./core.js";
import { renderAuth } from "./auth.js";
import { configureFeedPage, renderTags } from "./feed.js";
import { renderProfile } from "./profile.js";

async function start() {
  try {
    const sessionInfo = await requestJson("/api/session");
    state.viewer = sessionInfo.user;
  } catch (error) {
    document.getElementById("hero").append(element("p", "form-error", "Не удалось связаться с сервером. Обновите страницу."));
  }
  renderNavigation();
  if (state.page === "auth") renderAuth();
  else {
    if (state.page === "profile") await renderProfile();
    configureFeedPage();
    renderTags();
  }
}

start();
