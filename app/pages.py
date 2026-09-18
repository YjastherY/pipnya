from flask import Blueprint, redirect, render_template, url_for

pages = Blueprint("pages", __name__)


@pages.get("/")
@pages.get("/following")
@pages.get("/mine")
@pages.get("/saved")
def feed_page():
    return render_template("app.html", page="feed")


@pages.get("/profile/<username>")
def profile_page(username):
    return render_template("app.html", page="profile", profile_username=username)


@pages.get("/login")
@pages.get("/register")
def auth_page():
    return render_template("app.html", page="auth")


@pages.get("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="favicon.svg"))
