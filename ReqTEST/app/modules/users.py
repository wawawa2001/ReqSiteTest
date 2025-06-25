from flask import Blueprint, current_app as app, render_template
from flask_login import current_user
from app.models import User, Movie, UserIcon, Thumbnail, UserIntro, UserHeader, Cart, Follow, Review
from .db_common import get_reviews, get_icon_filename, get_item_review_info, creator_provided_movies_info
from datetime import datetime

users_bp = Blueprint("users", __name__)

def get_movieids(movies):
    movieids = [id.get_id() for id in movies]
    return movieids

def get_review_rating(reviews):
    review_ratings = [review.rating for review in reviews]

    if sum(review_ratings) == 0 or len(review_ratings) == 0:
        review_rating = 0
    else:
        review_rating = sum(review_ratings) / len(review_ratings)

    return review_rating

def get_isfollow(userid):
    is_follow = False
    if current_user.is_authenticated:
        follow = Follow.query.filter_by(creator_id=userid, follower_id=current_user.id).first()
        if follow:
            is_follow = True

    return is_follow

def get_common_data(userid):
    userintro = UserIntro.query.filter_by(userid=userid).first()
    if userintro:
        data = userintro.get_userpage_info()

    user = User.query.filter_by(id=userid).first()
    if user:
        data["username"] = user.username

    header_info = UserHeader.query.filter_by(userid=userid).first()
    if header_info:
        data["header_filename"] = header_info.header_filename
    else:
        data["header_filename"] = "default.png"

    icon_info = UserIcon.query.filter_by(userid=userid).first()
    if icon_info:
        data["icon_filename"] = icon_info.icon_filename
    else:
        data["icon_filename"] = "default.png"

    sales_figures = Cart.query.filter_by(user_id=userid, paid=1).count()
    data["sales_figures"] = sales_figures

    follower = Follow.query.filter_by(creator_id=userid).count()
    data["follower"] = follower

    return data

@users_bp.route("/users/<int:userid>/services")
def user_service(userid):
    data = get_common_data(userid)
    reviews = get_reviews(userid=userid)
    data["review_rating"] = get_review_rating(reviews)
    movies = Movie.query.filter_by(userid=userid).all()
    movies = creator_provided_movies_info(movies)

    return render_template("user_service.html", data=data, movies=movies, is_follow=get_isfollow(userid), reviews=reviews)


@users_bp.route("/users/<int:userid>/reviews")
def user_reviews(userid):
    data = get_common_data(userid)
    movies = Movie.query.filter_by(userid=userid).all()
    reviews = Review.query.filter(Review.movie_id.in_(get_movieids(movies))).all()
    data["review_rating"] = get_review_rating(reviews)

    tmp = []
    reviews = get_reviews(userid=userid)
    now = datetime.now()
    for review in reviews:
        review_dict = review.to_dict()
        review_dict["reviewer_icon_filename"] = get_icon_filename(review_dict["reviewer_id"])
        review_dict["title"] = review.movie.title
        if (now - review.created_at).days > 0:
            review_dict["before"] = str((now - review.created_at).days) + "日前"
        else:
            review_dict["before"] = str(int((now - review.created_at).seconds / 60 / 60)) + "時間前"
            
        tmp.append(review_dict)

    reviews = tmp

    return render_template("user_reviews.html", data=data, movies=creator_provided_movies_info(movies), is_follow=get_isfollow(userid), reviews=reviews)

@users_bp.route("/users/<int:userid>")
def userpage(userid):
    data = get_common_data(userid)
    movies = Movie.query.filter_by(userid=userid).all()
    reviews = Review.query.filter(Review.movie_id.in_(get_movieids(movies))).all()
    data["review_rating"] = get_review_rating(reviews)

    return render_template("user.html", data=data, movies=creator_provided_movies_info(movies), is_follow=get_isfollow(userid))