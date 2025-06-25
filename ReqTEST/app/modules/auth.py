from flask import Blueprint, render_template, request, redirect, url_for, current_app as app
from flask_login import current_user, login_required, logout_user, login_user
from app.models import User, TemporaryUser
from app import db
from uuid import uuid4

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    app.logger.info("Access Login")
    if current_user.is_authenticated:
        return redirect(url_for('view.index'))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)

            next_page = request.args.get("next")
            if not next_page or next_page == "/logout":
                return render_template(url_for("view.index"))

            return redirect(next_page)
        else:
            return render_template("login-register.html", msg="メールアドレスかパスワードが間違っています。")

    return render_template("login-register.html")

@auth_bp.route("/logout")
@login_required
def logout():
    app.logger.info("Access Logout.")
    logout_user()
    return redirect(url_for('auth.login'))
