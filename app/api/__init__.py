from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api")

from . import auth as auth
from . import posts as posts
from . import social as social
