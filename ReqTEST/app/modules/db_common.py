from flask import current_app as app
from app.models import UserIcon, User, UserIntro, Review, Thumbnail, Category
from app import db
from sqlalchemy import or_

def get_icon_filename(userid):
    filename = UserIcon.query.filter_by(userid=userid).first()
    if filename:
        filename = filename.icon_filename
    else:
        filename = "default.png"

    return filename


def exist_user(username, email):
    user = User.query.filter(
        or_(
            User.username == username,
            User.email == email
        )
    ).first()

    if not user:
        return False
    
    return user

def get_reviews(userid=None, movie_id=None):
    if userid is not None:
        reviews = Review.query.filter_by(userid=userid).all()
        return reviews

    if movie_id is not None:
        reviews = Review.query.filter_by(movie_id=movie_id).all()
        return reviews

    return False

def get_category_id(category_name):
    categoryid = None
    category = Category.query.filter_by(name=category_name).first()
    if category:
        categoryid = category.id

    return categoryid
    
def creator_provided_movies_info(movies):
    movie_list = []

    for movie in movies:
        movie = movie.to_dict()
        username = User.query.filter_by(id=movie["userid"]).first().username
        movie["username"] = username
        usericon = UserIcon.query.filter_by(userid=movie["userid"]).first()
        if not usericon:
            usericon = "default.png"
        else:
            usericon = usericon.icon_filename
        movie["usericon"] = usericon
        thum_filename = Thumbnail.query.filter_by(movie_id=movie["id"]).first().filename
        movie["thum_filename"] = thum_filename
        item_review = get_item_review_info(movie["id"])
        del item_review["review_info"]
        movie["item_review"] = item_review
        movie_list.append(movie)
    return movie_list

def set_thumbnail(movieid, filename):
    thumbnail = Thumbnail.query.filter_by(movie_id=movieid).first()
    if thumbnail:
        thumbnail.filename = filename
    else:
        thumbnail_obj = Thumbnail(
            movie_id = movieid,
            filename = filename
        )

        db.session.add(thumbnail_obj)
    
    db.session.commit()

def register_user(username, email):
    user = exist_user(username, email)
    print("This one", user)
    if user:
        print("すでに存在しています。")
        return user

    try:
        print("Start")
        user = User(
            username = username,
            email = email
        )
        db.session.add(user)
        db.session.commit()

        new_user_intro = UserIntro(
            userid=user.id
        )

        db.session.add(new_user_intro)
        db.session.commit()

        print("End")

        return user
    except Exception as e:
        print("This is Error")
        print(e)
        return False

def get_item_review_info(movieid):
    review_info = Review.query.filter_by(movie_id=movieid).all()
    review_count = 0
    review_ave = 0

    if review_info:
        review_count = len(review_info)
        
        review_sum = 0
        for review in review_info:
            review_sum += review.rating
        review_ave = round(review_sum / review_count, 1)

    review_data = {
        "review_info": review_info,
        "review_count": review_count,
        "review_ave": review_ave
    }

    return review_data