from app import db  # db を __init__.py からインポート
from datetime import datetime, timedelta
import bcrypt
import pytz
from flask_login import UserMixin

#GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_manager;
#GRANT ALL PRIVILEGES ON TABLE category TO app_manager;

def get_japan_time():
    tokyo_tz = pytz.timezone('Asia/Tokyo')
    return datetime.now(tokyo_tz)

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=get_japan_time)

    def to_id_name_dict(self):
        return {
            "id": self.id,
            "username": self.username
        }
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    # 必要に応じて、is_active プロパティをカスタマイズできます
    @property
    def is_active(self):
        return True  # すべてのユーザーをアクティブとみなす場合
    
    def get_id(self):
        return str(self.id)

class Follow(db.Model):
    __tablename__ = "follow"
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, nullable=False)
    follower_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'{self.creator_id} being followed by {self.follower_id}'

class MovieCache(db.Model):
    __tablename__ = "movie_cache"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)
    downloadedat = db.Column(db.DateTime(timezone=True), default=get_japan_time, nullable=False)

    def __repr__(self):
        return f'{self.filename} download at {self.downloadedAt}'

    
class UserIntro(db.Model):
    __tablename__ = "user_intro"

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    youtube = db.Column(db.String(100))
    intro_text = db.Column(db.String(1000))
    rating_1 = db.Column(db.Integer, default=0)
    rating_2 = db.Column(db.Integer, default=0)
    rating_3 = db.Column(db.Integer, default=0)
    rating_4 = db.Column(db.Integer, default=0)
    rating_5 = db.Column(db.Integer, default=0)
    favorite = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<UserIntro {self.userid}>'

    def get_userpage_info(self):
        return {
            "userid": self.userid,
            "youtube": self.youtube,
            "intro_text": self.intro_text,
            "rating_1": self.rating_1,
            "rating_2": self.rating_2,
            "rating_3": self.rating_3,
            "rating_4": self.rating_4,
            "rating_5": self.rating_5,
            "favorite": self.favorite
        }
    
class BankAccount(db.Model):
    __tablename__ = "bankaccounts"

    id = db.Column(db.Integer, primary_key=True)  # ID
    userid = db.Column(db.Integer, nullable=False)  # ユーザーID
    bank_code = db.Column(db.String(20), nullable=False)  # 金融機関コード
    bank_name = db.Column(db.String(100), nullable=False)  # 金融機関名
    branch_code = db.Column(db.String(20), nullable=False)  # 支店コード
    branch_name = db.Column(db.String(100), nullable=False)  # 支店名
    account_number = db.Column(db.String(30), nullable=False)  # 口座番号
    deposit_type = db.Column(db.String(20), nullable=False)  # 預金種類
    account_holder = db.Column(db.String(100), nullable=False)  # 口座名義
    account_holder_kana = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<BankAccount {self.userid}>'
    
class Movie(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    favorite = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2))
    req_price = db.Column(db.Numeric(10, 2))
    delivery_date = db.Column(db.Date)
    filename = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)

    creator = db.relationship('User', backref=db.backref('movies', lazy=True))
    thumbnails = db.relationship('Thumbnail', backref='movie', lazy=True)
    reviews = db.relationship('Review', backref='movie', lazy=True)

    category = db.relationship('Category', backref=db.backref('movie', lazy=True))

    def __repr__(self):
        return f'<Movie {self.title}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "userid": self.userid,
            "favorite": self.favorite,
            "description": self.description,
            "price": self.price,
            "req_price": self.req_price,
            "delivery_date": self.delivery_date,
            "category_id": self.category_id,
        }
    
    def to_short_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "userid": self.userid,
            "favorite": self.favorite,
            "price": self.price,
            "req_price": self.req_price,
            "delivery_date": self.delivery_date,
            "category_id": self.category_id,
        }

    def get_id(self):
        return self.id

class Thumbnail(db.Model):
    __tablename__ = "thumbnails"

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # ファイル名を格納するカラム

    def __repr__(self):
        return f'<Thumbnail {self.id} for Movie {self.movie_id}>'

class SampleLinks(db.Model):
    __tablename__ = "sample_links"

    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    url_link = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Thumbnail {self.id} for Movie {self.movie_id}>'
    
class User_favorite(db.Model):
    __tablename__ = "user_favorite"

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movieid = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)

    def __repr__(self):
        return f'<Userfavorite {self.id} for Movie {self.movieid}>'
    
class Category(db.Model):
    __tablename__ = "category"
    
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Category for {self.name}, {self.name}>'

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    comment = db.Column(db.Text)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # foreign_keys を明示的に指定
    creator = db.relationship('User', foreign_keys=[userid], backref=db.backref('created_movies', lazy=True))
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref=db.backref('written_reviews', lazy=True))

    def __repr__(self):
        return f'<Review {self.id} for Movie {self.movie_id}>'

    def to_dict(self):
        return {
            "id": self.id,
            "userid": self.userid,
            "movie_id": self.movie_id,
            "comment": self.comment,
            "reviewer_id": self.reviewer_id,
            "rating": self.rating,
            "created_at": self.created_at,
        }

class UserIcon(db.Model):
    __tablename__ = "usericons"

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    icon_filename = db.Column(db.String(255))

    user = db.relationship('User', backref=db.backref('icon', uselist=False, lazy=True))

    def __repr__(self):
        return f'<UserIcon for {self.userid}>'

class UserHeader(db.Model):
    __tablename__ = "userheaders"

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    header_filename = db.Column(db.String(255))

    def __repr__(self):
        return f'<UserHeader for {self.userid}>'
    
class TemporaryUser(db.Model):
    __tablename__ = "temporary_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=get_japan_time)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    def __init__(self, username, email, password, token):
        print(password)
        self.username = username
        self.email = email
        self.set_password(password)
        self.token = token
        self.expires_at = get_japan_time() + timedelta(hours=24)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash.encode("utf-8"))

    def __repr__(self):
        return '<TemporaryUser {}>'.format(self.username)
    
class Cart(db.Model):
    __tablename__ = "cart"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    added_at = db.Column(db.DateTime(timezone=True), default=get_japan_time)
    reqflg = db.Column(db.Integer)
    paid = db.Column(db.Integer)
    payid = db.Column(db.String(255))

    # リレーションシップ
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    movie = db.relationship('Movie', backref=db.backref('cart_items', lazy=True))

    def __repr__(self):
        return f'<Cart Item {self.id}: Movie {self.product_id}'
    
    def to_dict(self):
        return {
            "id": self.id,
            "userid": self.user_id,
            "product_id": self.product_id,
            "added_at": self.added_at,
            "reqflg": self.reqflg,
            "paid": self.paid,
            "created_at": self.payid,
            "movie": self.movie,
        }
        
class DirectMessage(db.Model):
    __tablename__ = "direct_messages"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime(timezone=True), default=get_japan_time)
    is_read = db.Column(db.Boolean, default=False)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # リレーションシップ
    cart = db.relationship('Cart', foreign_keys=[cart_id], backref=db.backref('conversation_msg', lazy=True))
    sender = db.relationship('User', foreign_keys=[sender_id], backref=db.backref('conversation_msg', lazy=True))

    def __repr__(self):
        return f'<DirectMessage {self.id}: From {self.sender_id}>'
    
    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "sent_at": self.sent_at,
            "is_read": self.is_read,
            "cart_id": self.cart_id,
            "sender_id": self.sender_id,
        }

class WordExplanations(db.Model):
    __tablename__ = "word_explanations"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(32), nullable=False)
    title_description = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)  # ファイル名を格納するカラム

    def __repr__(self):
        return f'<WordExplanations {self.id} for Explanation {self.title}>'