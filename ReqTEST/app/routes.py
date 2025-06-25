from flask import render_template, request, redirect, url_for, flash, send_file, Blueprint
from flask_login import login_user, login_required, current_user, logout_user
from app import db
from app.models import *
from .modules.PayPay import PayPay
from .modules.Stripe import PayMethods, check_payment_status
from werkzeug.utils import secure_filename
from uuid import uuid4
import os
from sqlalchemy.orm import joinedload, aliased, load_only, defer
from copy import deepcopy
from datetime import datetime
import uuid

import dropbox
import base64
from .modules.auth import auth_bp
from .modules.account import account_bp
from .modules.temp_view import view_bp
from .modules.register import register_bp
from .modules.pay_method import pay_method_bp
from .modules.cart import cart_bp
from .modules.db_common import get_icon_filename
from .modules.dm import dm_bp
from .modules.favorite import favorite_bp
from .modules.history import history_bp
from .modules.movies import movies_bp
from .modules.users import users_bp
from .modules.creators import creators_bp
from .modules.GoogleAuth import g_auth_bp
from .modules.YahooAuth import y_auth_bp
from .modules.conversation import conversation_bp

def init_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(view_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(pay_method_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(dm_bp)
    app.register_blueprint(favorite_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(creators_bp)
    app.register_blueprint(g_auth_bp)
    app.register_blueprint(y_auth_bp)
    app.register_blueprint(conversation_bp)

    @app.after_request
    def add_security_headers(response):
        response.headers.pop('Cross-Origin-Opener-Policy', None)
        response.headers.pop('Cross-Origin-Embedder-Policy', None)
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self' https://www.youtube.com https://www.youtube-nocookie.com;"
        response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'

        return response

