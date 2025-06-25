from flask import Blueprint, current_app as app, render_template, redirect, url_for
from flask_login import current_user
from app.models import User, User_favorite, Movie, UserIcon, Thumbnail

favorite_bp = Blueprint("favorite", __name__)

@favorite_bp.route("/favorite")
def user_favorite():
    if current_user.is_authenticated:
        user_favorite_data = User_favorite.query.filter_by(userid=current_user.id).all()

        movieids = [item.movieid for item in user_favorite_data]

        movies = Movie.query.filter(Movie.id.in_(movieids)).all()

        data = []
        for movie in movies:
            movie = movie.to_dict()

            usericon = UserIcon.query.filter_by(userid=movie["userid"]).first()
            if usericon:
                usericon = usericon.icon_filename
            else:
                usericon = "default.png"

            preview_filename = Thumbnail.query.filter_by(movie_id=movie["id"]).first().filename
            movie["thum_filename"] = preview_filename
            movie["usericon"] = usericon
            username = User.query.filter_by(id=movie["userid"]).first().username
            movie["username"] = username

            print(movie)
            data.append(movie)

        return render_template("favorite.html", movies=data)
    return redirect(url_for("auth.login"))