from flask import Blueprint, render_template, request, current_app as app, request
from flask_login import current_user
from app.models import Cart, Movie
from app import db
from .PayPay import PayPay
from .Stripe import PayMethods, check_payment_status
from sqlalchemy import case
from .common import is_valid_uuid

pay_method_bp = Blueprint("pay_method", __name__)

@pay_method_bp.route("/credit_pay_done", methods=["GET"])
def credit_pay_done():
    if current_user.is_authenticated:
        request.args.get("")

@pay_method_bp.route("/register_paypayid", methods=["GET"])
def register_paypayid():
    payid = request.args.get("merchant_payment_id")
    Cart.query.filter_by(user_id=current_user.id, paid=0).update({"payid": payid})
    db.session.commit()
    return "OK", 200


@pay_method_bp.route("/pay_status", methods=["GET"])
def pay_status():
    payid = Cart.query.filter_by(user_id=current_user.id).first().payid
    if is_valid_uuid(payid):
        if PayPay.payment_status(payid):
            Cart.query.filter_by(user_id=current_user.id).update({"paid": 1})
            db.session.commit()
            return render_template("pay.html", msg="OK")
        else:
            return render_template("pay.html", msg="NG")
    else:
        if check_payment_status(payid):
            Cart.query.filter_by(user_id=current_user.id).update({"paid": 1})
            db.session.commit()
            return render_template("pay.html", msg="OK")
        else:
            return render_template("pay.html", msg="NG")

@pay_method_bp.route("/error", methods=["GET"])
def error():
    return render_template("error.html")

@pay_method_bp.route("/pay", methods=["POST"])
def pay():
    # TODO 決済処理の仮組みなので本番注意！！！
    
    pay_methods = ["paypay", "credit"]
    pay_methods_route = [PayPay.create_qr_and_redirect, PayMethods.create_checkout_session]

    jsondata = request.get_json()
    pay_method = jsondata.get("select")

    if pay_method in pay_methods:
        
        cartinfo = db.session.query(
            Movie.id,
            Movie.title,
            Movie.filename,
            case(
                (Cart.reqflg==1, Movie.req_price),
                    else_=Movie.price).label("price")
        ).select_from(Cart).join(
            Movie, Cart.product_id==Movie.id
        ).filter(
            Cart.user_id == current_user.id,
            Cart.paid != 1
        )

        cartcnt = cartinfo.count()
        if cartcnt == 0:
            return {"url": app.config["HOST"]+"/cart", "msg": "カートは空です。"}, 200

        cartinfo = cartinfo.all()

        total = sum(item.price for item in cartinfo)
        
        pay_method_index = pay_methods.index(pay_method)

        if pay_method_index == 1:
            result = pay_methods_route[pay_method_index](int(total*1.1), current_user.email)
        else:
            result = pay_methods_route[pay_method_index](int(total*1.1))
        
        payid = result[0]
        url = result[-1]
        if not result:
            return {"url": app.config["ERROR_URL"], "msg": "エラーが起きました。"}, 200

        Cart.query.filter_by(user_id=current_user.id, paid=0).update({"payid": payid})
        db.session.commit()
        return {"url": url, "msg": ""}, 200