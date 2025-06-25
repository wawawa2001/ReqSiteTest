from flask import Blueprint, redirect, url_for, session, current_app as app
from flask_login import login_user
from authlib.integrations.flask_client import OAuth
from app import db
from app.models import User
import secrets
from .db_common import register_user

g_auth_bp = Blueprint("GoogleAuth", __name__)

def init_oauth():
    oauth = OAuth(app)
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_AUTH_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        client_kwargs={'scope': 'openid email profile'},
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
    )
    return google

@g_auth_bp.route('/login/google')
def login():
    google = init_oauth()
    # ランダムな nonce を生成し、セッションに保存
    nonce = secrets.token_urlsafe(16)
    session['nonce'] = nonce

    # Google認証リクエストに nonce を含める
    return google.authorize_redirect(
        url_for('GoogleAuth.auth_callback', _external=True),
        nonce=nonce
    )

@g_auth_bp.route('/google/auth/callback')
def auth_callback():
    google = init_oauth()
    try:
        # セッションに保存した nonce を取得
        nonce = session.pop('nonce', None)

        # IDトークンの検証時に nonce を渡す
        token = google.authorize_access_token()
        user_info = google.parse_id_token(token, nonce=nonce)
        user = register_user(user_info["name"], user_info["email"])

        print(user)
        if user:
            print("Register User")
            login_user(user, remember=True)
        return redirect(url_for('view.index'))
    except Exception as e:
        return f"An error occurred: {e}"