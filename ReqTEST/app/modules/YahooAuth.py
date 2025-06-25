from flask import Blueprint, redirect, url_for, session, jsonify, current_app as app
from authlib.integrations.flask_client import OAuth
import secrets

y_auth_bp = Blueprint("YahooAuth", __name__)

def init_oauth():
    oauth = OAuth(app)
    yahoo = oauth.register(
        name='yahoo',
        client_id=app.config["YAHOO_CLIENT_ID"],
        client_secret=app.config["YAHOO_CLIENT_SECRET"],
        authorize_url='https://api.login.yahoo.com/oauth2/request_auth',
        access_token_url='https://api.login.yahoo.com/oauth2/get_token',
        userinfo_endpoint='https://api.login.yahoo.com/openid/v1/userinfo',
        jwks_uri='https://api.login.yahoo.com/openid/v1/certs',  # 手動で設定
        client_kwargs={
            'scope': 'openid profile email',
        }
    )
    return yahoo

@y_auth_bp.route('/login/yahoo')
def login():
    yahoo = init_oauth()
    redirect_uri = url_for('YahooAuth.auth_callback', _external=True)
    return yahoo.authorize_redirect(redirect_uri)

@y_auth_bp.route('/yahoo/auth/redirect')
def auth_callback():
    yahoo = init_oauth()
    token = yahoo.authorize_access_token()
    resp = yahoo.get('https://api.login.yahoo.com/openid/v1/userinfo')
    user_info = resp.json()
    return jsonify(user_info)