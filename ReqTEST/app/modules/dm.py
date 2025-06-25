from flask import Blueprint, request, current_app as app, request, render_template, redirect, url_for
from flask_login import current_user
from app.models import DirectMessage, User
from app import db
from sqlalchemy.orm import aliased
from sqlalchemy import func, or_, and_, desc
from .db_common import get_icon_filename

# TODO COMMON GET_ICON_FILENAME

dm_bp = Blueprint("dm", __name__)

@dm_bp.route("/dm")
def get_dmlist():
    if current_user.is_authenticated:

        sender_alias = aliased(User)
        recipient_alias = aliased(User)

        data = (
            db.session.query(
                DirectMessage.sender_id,
                sender_alias.username.label('sender_username'),
                DirectMessage.recipient_id,
                recipient_alias.username.label('recipient_username'),
                DirectMessage.message,
                DirectMessage.sent_at,
                DirectMessage.is_read
            )
            .join(sender_alias, sender_alias.id == DirectMessage.sender_id)  # sender_idに基づいてusersテーブルを結合
            .join(recipient_alias, recipient_alias.id == DirectMessage.recipient_id)  # recipient_idに基づいてusersテーブルを結合
            .filter(
                or_(
                    DirectMessage.sender_id == current_user.id,
                    DirectMessage.recipient_id == current_user.id
                )
            )
            .order_by(
                func.least(DirectMessage.sender_id, DirectMessage.recipient_id),
                func.greatest(DirectMessage.sender_id, DirectMessage.recipient_id),
                DirectMessage.sent_at.desc()  # 最新のメッセージから順番に並べる
            )
            .distinct(func.least(DirectMessage.sender_id, DirectMessage.recipient_id), func.greatest(DirectMessage.sender_id, DirectMessage.recipient_id))  # 各グループごとに1つだけ取得
            .all()
        )

        dmlist = []

        for dm in data:
            pair = [dm.sender_id, dm.recipient_id]
            pair.remove(current_user.id)
            someone_id = pair[0]
            user = User.query.filter_by(id=someone_id).first()
            someone_username = user.to_id_name_dict()["username"]
            icon_filename = get_icon_filename(someone_id)
            

            data = {
                "someone_id": someone_id,
                "someone_username": someone_username,
                "message": dm.message,
                "sent_at": dm.sent_at,
                "is_read": dm.is_read,
                "icon_filename": icon_filename
            }

            dmlist.append(data)


        return render_template("dm.html", dmlist=dmlist)
    return redirect(url_for("auth.login"))

@dm_bp.route("/get_dm", methods=["POST"])
def get_dm():
    jsondata = request.get_json()
    if "userid" in jsondata:
        userid = jsondata.get("userid")

    messages = DirectMessage.query.filter(or_(
        and_(
            DirectMessage.sender_id == userid,
            DirectMessage.recipient_id == current_user.id
        ),
        and_(
            DirectMessage.sender_id == current_user.id,
            DirectMessage.recipient_id == userid
        )
    ))

    print("This!!!")

    return {"data": messages}, 200

@dm_bp.route("/post_dm", methods=["POST"])
def post_dm():
    jsondata = request.get_json()
    pair = jsondata.get("pair")
    text = jsondata.get("text")

    pair.remove(current_user.username)
    recipient_name = pair[0]
    sender_id = current_user.id

    recipient_id = User.query.filter_by(username=recipient_name).first().id

    dm = DirectMessage(
        sender_id = sender_id,
        recipient_id = recipient_id,
        message = text,
    )

    db.session.add(dm)
    db.session.commit()


    return {"msg": "OK"}, 200