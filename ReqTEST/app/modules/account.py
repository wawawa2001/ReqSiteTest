from flask import Blueprint, current_app as app, request, render_template, redirect, url_for
from flask_login import current_user
from app.models import User, UserIcon, UserHeader, Cart, UserIntro, BankAccount, User_favorite, Movie, Follow
from app import db
from uuid import uuid4
from werkzeug.utils import secure_filename
import os
import base64

account_bp = Blueprint('account', __name__)

def link_normarize(text, option=None):
    if option is not None:
        text = text.split(option)[-1]

    text = text.split("/")[0]
    text = text.split("?")[0]

    return text

@account_bp.route("/account", methods=["GET", "POST"])
def account_settings():
    umsg = None
    mmsg = None
    app.logger.info("Access Account Page.")
    if not current_user.is_authenticated:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        print("ACCOUNT ___ POST")
        
        youtube_link = link_normarize(request.form.get("youtube_link"), "youtube.com/")
        self_intro = request.form.get("self_intro")

        userintro = UserIntro.query.filter_by(userid=current_user.id).first()

        if not userintro:
            print("ADD USERINTRO")

            userintro = UserIntro(
                userid = current_user.id,
                youtube = youtube_link,
                intro_text = self_intro,
            )

            db.session.add(userintro)

        else:
            print("UPDATE USERINTRO")

            userintro.youtube = youtube_link
            userintro.intro_text = self_intro
        
        db.session.commit()

        iconfile = request.files["icon"]
        extension = iconfile.filename.split(".")[-1]

        username = request.form.get("username")
        email = request.form.get("email")

        if not username == current_user.username:

            user = User.query.filter_by(username=current_user.username).first()
            icon_table = UserIcon.query.filter_by(userid=current_user.id).first()
            
            if user:
                is_exist = User.query.filter_by(username=username).first()
                if not is_exist:
                    user.username = username
                    icon_table.userid = current_user.id
                    db.session.commit()
                else:
                    umsg = "すでに使用されているユーザネームです。"

        if not email == current_user.email:

            user = User.query.filter_by(email=current_user.email).first()
            
            if user:
                is_exist = User.query.filter_by(email=email).first()
                if not is_exist:
                    user.email = email
                    db.session.commit()
                else:
                    mmsg = "すでに使用されているメールアドレスです。"

        random_name = uuid4().hex
        filename = secure_filename(random_name)

        basepath = os.path.join(app.config['USER_ICON_FOLDER'])

        iconpath = os.path.join(basepath, filename+"."+extension)
        iconfile.save(iconpath)

        icon_table = UserIcon.query.filter_by(userid=current_user.id).first()
        if iconfile:
            if icon_table:
                icon_table.username = current_user.username
                if os.path.exists(os.path.join(basepath,icon_table.icon_filename)):
                    os.remove(os.path.join(basepath,icon_table.icon_filename))
                icon_table.icon_filename = filename+"."+extension

                db.session.commit()
            else:
                icon = UserIcon(
                    userid = current_user.id,
                    icon_filename = filename+"."+extension
                )

                db.session.add(icon)

                db.session.commit()

        cropped_image = request.form.get('cropped-image')
    
        if cropped_image:
            # base64のヘッダー部分を除く
            image_data = cropped_image.split(",")[1]
            
            # MIMEタイプの判別
            mime_type = cropped_image.split(";")[0].split(":")[1]
            
            # MIMEタイプに基づいて拡張子を決定
            if mime_type == 'image/jpeg':
                extension = 'jpg'
            elif mime_type == 'image/png':
                extension = 'png'
            else:
                return jsonify({'error': 'サポートされていない画像形式です'}), 400
            
            # base64データをデコード
            image = base64.b64decode(image_data)
            
            # ランダムなファイル名を生成
            random_name = uuid4().hex
            filename = secure_filename(random_name)  # 安全なファイル名にする
            
            # 保存先のパスを作成
            basepath = os.path.join(app.config['USER_HEADER_FOLDER'])
            
            # 画像を保存するパスを決定
            headerpath = os.path.join(basepath, filename + "." + extension)
            
            # 画像を保存
            with open(headerpath, 'wb') as file:
                file.write(image)

            header_table = UserHeader.query.filter_by(userid=current_user.id).first()
            if cropped_image:
                if header_table:
                    header_table.username = current_user.username
                    if os.path.exists(os.path.join(basepath,header_table.header_filename)):
                        os.remove(os.path.join(basepath,header_table.header_filename))
                    header_table.header_filename = filename+"."+extension

                    db.session.commit()
                else:
                    header = UserHeader(
                        userid = current_user.id,
                        header_filename = filename+"."+extension
                    )

                    db.session.add(header)
                    db.session.commit()

        bank_code = request.form.get('bank_code')
        bank_name = request.form.get('bank_name')
        branch_code = request.form.get('branch_code')
        branch_name = request.form.get('branch_name')
        account_number = request.form.get('account_number')
        deposit_type = request.form.get('deposit_type')
        account_holder = request.form.get('account_holder')
        account_holder_kana = request.form.get('account_holder_kana')

        bankac = BankAccount.query.filter_by(userid=current_user.id).first()
        if bankac:
            bankac.bank_code = bank_code
            bankac.bank_name = bank_name
            bankac.branch_code = branch_code
            bankac.branch_name = branch_name
            bankac.account_number = account_number
            bankac.deposit_type = deposit_type
            bankac.account_holder = account_holder
            bankac.account_holder_kana = account_holder_kana
        else:
            bankac = BankAccount(
                userid = current_user.id,
                bank_code = bank_code,
                bank_name = bank_name,
                branch_code = branch_code,
                branch_name = branch_name,
                account_number = account_number,
                deposit_type = deposit_type,
                account_holder = account_holder,
                account_holder_kana = account_holder_kana
            )

            db.session.add(bankac)
            db.session.commit()
    
    icon_filename = UserIcon.query.filter_by(userid=current_user.id).first()
    if not icon_filename:
        icon_filename = "default.png"
    else:
        icon_filename = icon_filename.icon_filename

    header_filename = UserHeader.query.filter_by(userid=current_user.id).first()
    if not header_filename:
        header_filename = "default.png"
    else:
        header_filename = header_filename.header_filename
        
    userdata = [
        current_user.username,
        current_user.email,
    ]

    cart = Cart.query.filter_by(user_id = current_user.id).with_entities(Cart.product_id).all()
    cart = [item[0] for item in cart]
    cart = list(set(cart))

    userintro = UserIntro.query.filter_by(userid=current_user.id).first()

    bankaccount = BankAccount.query.filter_by(userid=current_user.id).first()

    return render_template("account.html", userdata=userdata, header_filename=header_filename, icon_filename=icon_filename, cart=cart, userintro=userintro, umsg=umsg, mmsg=mmsg, bankaccount=bankaccount)

@account_bp.route("/follow", methods=["POST"])
def follow():
    if current_user.is_authenticated:
        creator_id = int(request.get_json())
        
        follow = Follow.query.filter_by(creator_id=creator_id, follower_id=current_user.id).first()
        if follow:
            is_follow = False
            db.session.delete(follow)
            db.session.commit()
        else:
            is_follow = True
            follow = Follow(
                creator_id = creator_id,
                follower_id = current_user.id
            )

            db.session.add(follow)
            db.session.commit()

        follower = Follow.query.filter_by(creator_id=creator_id).count()

        return {"is_follow": is_follow, "msg": "", "follower": follower}, 200
    return {"is_follow": False, "msg": "ログインしてください。"}, 200



@account_bp.route("/user_favorite_judge", methods=["POST"])
def user_favorite_judge():
    msg = None
    movie_id = request.get_json()
    favorite_flg = False

    if current_user.is_authenticated:
        user_id = current_user.id

        user_favorite_data = User_favorite.query.filter_by(userid=user_id, movieid=movie_id).first()

        if not user_favorite_data:
            favorite_flg = True
            user_favorite = User_favorite(
                userid = user_id,
                movieid = movie_id
            )

            db.session.add(user_favorite)
            db.session.commit()

            movie = Movie.query.filter_by(id=movie_id).first()

            if movie:
                movie.favorite += 1
                db.session.commit()
        else:
            db.session.delete(user_favorite_data)
            db.session.commit()

            movie = Movie.query.filter_by(id=movie_id).first()

            if movie:
                movie.favorite -= 1
                db.session.commit()
    else:
        msg = "お気に入りに追加するにはログインしてください。"
        
    movie = Movie.query.filter_by(id=movie_id).first()
    
    return {"favorite": str(movie.favorite), "msg": msg, "favotite_flg": favorite_flg}, 200