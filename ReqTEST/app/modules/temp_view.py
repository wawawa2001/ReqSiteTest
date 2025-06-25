from flask import current_app as app, render_template, Blueprint
from app.models import WordExplanations

view_bp = Blueprint("view", __name__)

@view_bp.route("/front")
def front():
    app.logger.info("Access Front.")
    return render_template("front.html")

@view_bp.route("/")
@view_bp.route("/index")
@view_bp.route("/top")
def index():
    app.logger.info("Access Index Page.")
    return render_template("front.html")

@view_bp.route("/explanation")
def explanation():
    explanations = WordExplanations.query.all()
    return render_template("explanation.html", explanations=explanations)

@view_bp.route("/illusts")
def illusts():
    app.logger.info("Access Illust.")
    return render_template("illusts.html")