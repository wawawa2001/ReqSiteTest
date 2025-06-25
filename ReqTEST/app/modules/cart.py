from flask import Blueprint, request, current_app as app, render_template, redirect, url_for
from flask_login import current_user
from app.models import Cart, Movie, Thumbnail, User, UserIcon
from app import db
from sqlalchemy import and_

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/cart")
def cart():
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id = current_user.id).with_entities(Cart.product_id).all()
        cart = [item[0] for item in cart]
        cart = list(set(cart))

        cartinfo = Cart.query.filter(
            and_(
                Cart.user_id == current_user.id,
                Cart.paid != 1
            )
        )

        cart_p_ids = [pid.product_id for pid in cartinfo]
        print(cart_p_ids)

        movies = Movie.query.filter(Movie.id.in_(cart_p_ids)).all()

        print(movies)

        data = []

        for movie in movies:
            thum_filename = Thumbnail.query.filter_by(movie_id=movie.id).first().filename
            movie = movie.to_dict() 
            print(movie)
            username = User.query.filter_by(id=movie["userid"]).first().username
            usericon = UserIcon.query.filter_by(userid=movie["userid"]).first()
            if usericon:
                icon_filename = usericon.icon_filename
            else:
                icon_filename = "default.png"
            movie["username"] = username
            movie["filename"] = thum_filename
            movie["icon_filename"] = icon_filename
            data.append(movie)

        total = 0
        
        for item in data:
            if item["price"] is None:
                total = total + item["req_price"]
            else:
                total = total + item["price"]

        return render_template("cart.html", movies=data, total=total)
    return redirect(url_for("auth.login"))

@cart_bp.route("/get_cart")
def get_cart():
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id = current_user.id, paid=0).with_entities(Cart.product_id).all()
        cart = [item[0] for item in cart]
        cart = list(set(cart))
        cnt = len(cart)

        return {"cartcnt": str(cnt)}, 200
    else:
        return {"cartcnt": str(0)}, 200
    
@cart_bp.route("/add_req", methods=["POST"])
def add_req():
    def cart_count():
        cnt = 0
        if current_user.is_authenticated:
            cart = Cart.query.filter_by(user_id = current_user.id).with_entities(Cart.product_id).all()
            cart = [item[0] for item in cart]
            cart = list(set(cart))
            cnt = len(cart)
        return cnt

    if request.method == "POST":
        if request.get_json():
            item_id = request.get_json()

            if item_id:
                item_id = item_id[0]

            cnt = cart_count()

            cart = Cart.query.filter_by(user_id = current_user.id, product_id = item_id).first()

            if cart:
                if cart.paid == 0:
                    return {"msg":"すでに商品がカートに入っています。", "cartcnt": str(cnt)}, 200
                else:
                    return {"msg":"すでに購入履歴のある商品です。購入履歴ページよりご確認ください。", "cartcnt": str(cnt)}, 200

            cart = Cart(
                user_id = current_user.id,
                product_id = item_id,
                reqflg = 1,
                paid = 0,
            )

            db.session.add(cart)
            db.session.commit()

            cnt = cart_count()
                
        return {"msg":"カートに追加されました！", "cartcnt": str(cnt)}, 200
    
@cart_bp.route("/add_cart", methods=["POST"])
def add_cart():
    if not current_user.is_authenticated:
        return {"msg":"ログインしてください。", "cartcnt": str(0)}, 200

    def cart_count():
        cnt = 0
        if current_user.is_authenticated:
            cart = Cart.query.filter_by(user_id = current_user.id).with_entities(Cart.product_id).all()
            cart = [item[0] for item in cart]
            cart = list(set(cart))
            cnt = len(cart)
        return cnt

    if request.method == "POST":
        if request.get_json():
            item_id = request.get_json()

            if item_id:
                item_id = item_id[0]

            cnt = cart_count()

            cart = Cart.query.filter_by(user_id = current_user.id, product_id = item_id).first()

            if cart:
                if cart.paid == 0:
                    return {"msg":"すでに商品がカートに入っています。", "cartcnt": str(cnt)}, 200
                else:
                    return {"msg":"すでに購入履歴のある商品です。購入履歴ページよりご確認ください。", "cartcnt": str(cnt)}, 200

            cart = Cart(
                user_id = current_user.id,
                product_id = item_id,
                paid = 0,
            )

            db.session.add(cart)
            db.session.commit()

            cnt = cart_count()
                
        return {"msg":"カートに追加されました！", "cartcnt": str(cnt)}, 200

@cart_bp.route("/delitem", methods=["POST"])
def delitem():
    itemid = request.get_json()
    itemid = itemid.get("itemid")

    Cart.query.filter_by(user_id = current_user.id, product_id=itemid).delete()
    db.session.commit()

    return {"msg": "Deleted."}, 200