from flask import Blueprint, current_app as app, render_template, flash, request, redirect, url_for
from flask_login import current_user
from app.models import User, Movie, UserIcon, Thumbnail, Review, User_favorite, SampleLinks
from .db_common import get_item_review_info

movies_bp = Blueprint("movies", __name__)

@movies_bp.route("/movies/<int:movieid>")
def movie(movieid):
    id = movieid
    movie = Movie.query.filter_by(id=id).first()

    if movie:
        movie = movie.to_dict()
    else:
        return redirect(url_for("movies"))
    
    username = User.query.filter_by(id=movie["userid"]).first().username
    movie["username"] = username
    usericon = UserIcon.query.filter_by(userid=movie["userid"]).first()

    if not usericon:
        usericon = "default.png"
    else:
        usericon = usericon.icon_filename

    preview_filename = Thumbnail.query.filter_by(movie_id=movie["id"]).first().filename

    review_data = get_item_review_info(movie["id"])

    favorite_flg = False
    if current_user.is_authenticated and User_favorite.query.filter_by(userid=current_user.id, movieid=movie["id"]).first():
        favorite_flg = True

    print(favorite_flg)
    sample_links = SampleLinks.query.filter_by(movie_id=movie["id"]).all()
    sample_links = [link.url_link for link in sample_links] + [None] * (3 - len(sample_links))

    print("Test")
    print(sample_links)

    return render_template("item.html", movie=movie, usericon=usericon, preview_filename=preview_filename, review_data=review_data, favorite_flg=favorite_flg, sample_links=sample_links)


@movies_bp.route("/movies", methods=["GET"])
def movies():
    app.logger.info("Access Movies.")
    try:
        if "category" in request.args:
            category_id = int(request.args["category"])
            if category_id == 1:
                movies = Movie.query.all()
            else:
                movies = Movie.query.filter_by(category_id=category_id).all()
        else:
            movies = Movie.query.all()

        if "search" in request.args:
            print("P2")
            text = request.args.get("search")
            movies = [movie for movie in movies if text.lower() in movie.title.lower()]

            print(movies)

        print("P3")

        data = []


        for movie in movies:
            movie = movie.to_dict()

            print("P4")
            print(movie["userid"])
            print(User.query.filter_by(id=movie["userid"]).first())


            username = User.query.filter_by(id=movie["userid"]).first().username

            print("P5")

            movie["username"] = username

            usericon = UserIcon.query.filter_by(userid=movie["userid"]).first()

            if not usericon:
                usericon = "default.png"
            else:
                usericon = usericon.icon_filename

            movie["usericon"] = usericon


            thum_filename = Thumbnail.query.filter_by(movie_id=movie["id"]).first().filename

            movie["thum_filename"] = thum_filename

            print(movie)

            data.append(movie)

        return render_template("movies.html", movies=data)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        flash('データの取得中にエラーが発生しました。', 'error')
        return render_template("movies.html", movies=[])