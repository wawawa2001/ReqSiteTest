from flask import Blueprint, current_app as app, render_template, request, redirect, url_for
from flask_login import current_user
from app.models import DirectMessage
from sqlalchemy import asc
from app import db

conversation_bp = Blueprint("conversation", __name__)

@conversation_bp.route("/conversations")
def conversations():
    if current_user.is_authenticated:
        return render_template("conversations.html")
    else:
        return redirect(url_for("auth.login"))

@conversation_bp.route("/conversation/<int:movie_id>", methods=["GET"])
def conversation(movie_id):
    if current_user.is_authenticated:
        return render_template("conversation.html")
    else:
        return redirect(url_for("auth.login"))

@conversation_bp.route("/post_msg", methods=["POST"])
def post_msg():
    if current_user.is_authenticated:
        text = request.get_json()["text"]
        cart_id = request.get_json()["conversation_id"]
        msg = DirectMessage(
            message = text,
            cart_id = cart_id,
            sender_id = current_user.id
        )

        db.session.add(msg)
        db.session.commit()

        return "OK", 200

@conversation_bp.route("/get_msgs", methods=["GET"])
def get_messages():
    if current_user.is_authenticated:
        if "conversation_id" in request.args:
            cart_id = int(request.args.get("conversation_id"))
        messages = DirectMessage.query.filter_by(cart_id=cart_id).order_by(asc(DirectMessage.sent_at)).all()

        data = []
        for msg in messages:
            msg_dict = msg.to_dict()
            if msg_dict["sender_id"] == current_user.id:
                msg_dict["me"] = True
            else:
                msg_dict["me"] = False
            data.append(msg_dict)
            
    return {"messages": data}, 200