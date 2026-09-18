import { state, element, requestJson, showError, makeLink } from "./core.js";

export function renderAuth() {
  if (state.viewer) {
    location.href = "/";
    return;
  }
  const registering = location.pathname === "/register";
  document.getElementById("auth-panel").hidden = false;
  document.getElementById("sidebar").hidden = true;
  document.getElementById("main-grid").classList.add("auth-layout");
  document.getElementById("hero").classList.add("auth-hero");
  document.getElementById("page-title").textContent = registering ? "Каждая мысль заслуживает света." : "Снова на связи.";
  document.getElementById("page-description").textContent = registering ? "Создайте профиль, чтобы делиться открытиями и собирать свою ленту." : "Войдите, чтобы продолжить общение и вернуться к сохранённым заметкам.";
  document.getElementById("auth-title").textContent = registering ? "Создать аккаунт" : "Войти в аккаунт";
  document.getElementById("auth-submit").textContent = registering ? "Зарегистрироваться" : "Войти";
  document.getElementById("username-field").hidden = !registering;
  document.getElementById("email-field").hidden = !registering;
  document.getElementById("identity-field").hidden = registering;
  document.querySelector('[name="password"]').autocomplete = registering ? "new-password" : "current-password";
  const switcher = document.getElementById("auth-switch");
  switcher.textContent = registering ? "Уже есть аккаунт? " : "Ещё нет аккаунта? ";
  switcher.append(makeLink(registering ? "/login" : "/register", registering ? "Войти" : "Зарегистрироваться"));
  document.getElementById("auth-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const data = registering
      ? { username: form.get("username"), email: form.get("email"), password: form.get("password") }
      : { identity: form.get("identity"), password: form.get("password") };
    const submit = document.getElementById("auth-submit");
    submit.disabled = true;
    showError(document.getElementById("auth-error"), "");
    try {
      await requestJson(registering ? "/api/register" : "/api/login", { method: "POST", body: JSON.stringify(data) });
      location.href = "/";
    } catch (error) {
      showError(document.getElementById("auth-error"), error.message);
      submit.disabled = false;
    }
  });
}

