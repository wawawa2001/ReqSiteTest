from flask import Blueprint, current_app as app, render_template, request, send_file
from flask_login import current_user
from app.models import User, Movie, UserIcon, Thumbnail, Cart, MovieCache
import os
from .GoogleDrive import GoogleDriveClass
from uuid import uuid4
from datetime import datetime
import pytz
from app import db

history_bp = Blueprint("history", __name__)

def get_japan_time():
    tokyo_tz = pytz.timezone('Asia/Tokyo')
    return datetime.now(tokyo_tz)

@history_bp.route("/history")
def history():
    if current_user.is_authenticated:
        
        paid_cart = Cart.query.filter_by(user_id=current_user.id, paid=1).all()

        history = []
        for cart in paid_cart:
            movie = cart.movie.to_dict()
            movie["conversation"] = cart.id
            movie["reqflg"] = cart.reqflg
            movie["thum_filename"] = cart.movie.thumbnails[0].filename
            movie["username"] = cart.movie.creator.username
            if cart.movie.creator.icon:
                movie["usericon"] = cart.movie.creator.icon.icon_filename
            else:
                movie["usericon"] = "default.png"

            history.append(movie)

        return render_template("history.html", history=history)
    else:
        return redirect(url_for("auth.login"))

def update_cache(filename):
    print("UPDATE!!!")
    cache = MovieCache.query.filter_by(filename=filename).first()
    cache.downloadedat = get_japan_time()
    db.session.commit()


def add_cache(filename):
    print("ADD!!!")
    cache = MovieCache.query.filter_by(filename=filename).first()
    if cache:
        update_cache(filename)
    else:
        cache = MovieCache(
            filename=filename
        )

        db.session.add(cache)
        db.session.commit()

    

# キャッシュ方式（？）
# 動画コンテンツをキャッシュフォルダーに保存する（最終ダウンロード日時を保存）
# キャッシュになければGoogleからダウンロードする。

# ダウンロード可能条件
# ログインしているかどうか
# ログインしていた場合、対応表を用いて仮URLを渡す
# 仮URLにアクセスしてきた際に対応表を用いて本ファイル名
# 購入済みか確認
@history_bp.route("/history/download")
def download():
    if current_user.is_authenticated and "id" in request.args:
        mov_id = request.args.get("id")

        filename = Movie.query.filter_by(id=mov_id).with_entities(Movie.filename).first()[0]
        filepath = os.path.join(app.config['MOVIE_FOLDER'], "original", filename)
        if not os.path.exists(filepath):
            GoogleDriveClass().download(filename)
            add_cache(filename)
        else:
            update_cache(filename)
        extf = str(uuid4())
        extension = filename.split(".")[-1]

    return send_file(filepath, as_attachment=True, download_name=extf+"."+extension)
