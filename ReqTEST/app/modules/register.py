from flask import Blueprint, render_template, request, redirect, url_for, current_app as app
from flask_login import current_user, login_required, logout_user, login_user
from app.models import User, TemporaryUser, UserIntro
from app import db
from uuid import uuid4
from .sendmail import SendMail
import os
from datetime import datetime
import pytz

register_bp = Blueprint('register', __name__)
def_path = "def_register"

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    app.logger.info("Access Register.")
    if request.method == "POST":
        jsondata = request.get_json()
        username = jsondata.get("username")
        email = jsondata.get("email")
        password = jsondata.get("password")
        confirm_password = jsondata.get("confirm_password")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return {"msg": "このユーザ名はすでに使用されています。"}, 200

        existing_user = TemporaryUser.query.filter_by(username=username).first()
        if existing_user:
            return {"msg": "このユーザ名はすでに使用されています。"}, 200
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {"msg": "このメールアドレスはすでに使用されています。"}, 200
            
        existing_user = TemporaryUser.query.filter_by(email=email).first()
        if existing_user:
            return {"msg": "このメールアドレスはすでに使用されています。"}, 200

        if password != confirm_password:
            return {"msg": "パスワードが一致しません。"}, 200
    
        token = str(uuid4())
        temp_user = TemporaryUser(username=username, email=email, password=password, token=token)
        db.session.add(temp_user)
        db.session.commit()

        register_link = os.path.join(app.config["HOST"], def_path)
        SendMail.send_email(email, "仮登録完了メール", f"仮登録が完了いたしました。下記のリンクにアクセスし、本登録を完了してください。\n{register_link}?token={token}")

        return {"msg": "仮登録が完了しました。メールボックスを確認し、本登録に進んでください。"}, 200

    return render_template("login-register.html", msg="")

@register_bp.route("/def_register")
def def_register():
    app.logger.info("Access Define User.")
    token = request.args.get("token", None)
    if not token:
        return render_template("login-register.html", msg="無効なトークンです。")

    temp_user = TemporaryUser.query.filter_by(token=token).first()
    if not temp_user:
        return render_template("login-register.html", msg="無効なトークンです。")

    if temp_user.expires_at < datetime.utcnow():
        db.session.delete(temp_user)
        db.session.commit()
        return render_template("login-register.html", msg="トークンの有効期限が切れています。再度登録をしてください。")

    try:
        # 本登録ユーザーの作成
        new_user = User(
            username=temp_user.username,
            email=temp_user.email,
            password_hash=temp_user.password_hash,
            created_at=datetime.utcnow()
        )
    
        # 新しいユーザーを追加し、一時ユーザーを削除、また、UserIntroも作成。
        db.session.add(new_user)
        db.session.delete(temp_user)
        db.session.commit()

        new_user_intro = UserIntro(
            userid=new_user.id
        )

        db.session.add(new_user_intro)
        db.session.commit()

        return render_template("login-register.html", msg="本登録が完了しました。ログインしてください。")
    except Exception as e:
        db.session.rollback()
        print(f"Error during registration: {str(e)}")
        return render_template("login-register.html", msg="登録中にエラーが発生しました。再度お試しください。")
