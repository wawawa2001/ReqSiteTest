from flask import Blueprint, current_app as app, render_template, request, redirect, url_for
from flask_login import current_user
from app.models import User, Movie, UserIcon, Thumbnail, Category, SampleLinks
from .db_common import creator_provided_movies_info, get_category_id, set_thumbnail
from flask_cors import cross_origin
from uuid import uuid4
from werkzeug.utils import secure_filename
import os
from .GoogleDrive import GoogleDriveClass
from app import db

creators_bp = Blueprint("creators", __name__)


@creators_bp.route("/my_contents", methods=["GET", "POST"])
def my_contents():
    movies = Movie.query.filter_by(userid=current_user.id).all()
    movies = creator_provided_movies_info(movies)
    return render_template("my_contents.html", movies=movies)

@creators_bp.route("/my_contents/<int:movieid>", methods=["GET", "POST"])
def edit_my_content(movieid):

    if current_user.is_authenticated:
        basepath = os.path.join(app.config['MOVIE_FOLDER'])
        movie = Movie.query.filter_by(id=movieid).first()
        thumbnail = Thumbnail.query.filter_by()

        if request.method == "POST":

            # サムネイル保存
            thumbnail = request.files["thum"]
            if thumbnail.filename:
                extension = thumbnail.filename.split(".")[-1]
                random_name = uuid4().hex
                thumbnail_name = secure_filename(random_name)+"."+extension
                ppath = os.path.join(basepath, "preview", thumbnail_name)
                thumbnail.save(ppath)
                set_thumbnail(movieid, thumbnail_name)
                
            # Links
            sample = request.form.getlist("sample")
            sample = [url for url in sample if url.strip()]
            sample = [mID.split("?v=")[1][:11] for mID in sample]

            # Delete Old Links
            old_sample = SampleLinks.query.filter_by(movie_id=movieid).all()
            for link in old_sample:
                db.session.delete(link)

            db.session.commit()

            # Add New Links
            for link in sample:
                linkobj = SampleLinks(
                    movie_id = movieid,
                    url_link = link
                )
                db.session.add(linkobj)

            db.session.commit()

            movie.title = request.form.get("title")
            tags = request.form.get("tags")
            print("TAG:", tags)
            category_id = get_category_id(tags)
            print(category_id)
            movie.category_id = category_id
            movie.description = request.form.get("description")

            if request.form.get("content"):
                fullmovie = request.files["full"]
                extension = fullmovie.filename.split(".")[-1]
                random_name = uuid4().hex
                fullmovie_name = secure_filename(random_name)+"."+extension

                opath = os.path.join(basepath, "original", fullmovie_name)
                movie.price = int(request.form.get("price"))

                fullmovie.save(opath)
                GoogleDriveClass().upload(fullmovie_name)
                movie.fullmovie_name = fullmovie_name
            else:
                movie.req_price = int(request.form.get("price"))
                fullmovie_name = None
                
            db.session.commit()

            referrer = request.referrer 
            if not referrer:
                referrer = url_for('creators_bp.movie')

            return redirect(referrer)


        movie = Movie.query.filter_by(userid=current_user.id, id=movieid).first()
        sample_links = SampleLinks.query.filter_by(movie_id=movieid).all()
        sample_links = ["https://www.youtube.com/watch?v="+link.url_link for link in sample_links]

        thum_filename = Thumbnail.query.filter_by(movie_id=movieid).first()
        if thum_filename:
            thum_filename = thum_filename.filename
        else:
            thum_filename = ""

        while len(sample_links) < 3:
            sample_links.append("") 
        
        category_select_flg = [""] * 7
        category_select_flg[movie.category.id] = "selected"

        if movie:
            data = {
                "thum_filename": thum_filename,
                "title": movie.title,
                "category": category_select_flg,
                "description": movie.description,
                "price": movie.price or movie.req_price,
                "content": movie.filename,
                "sample_links": sample_links
            }

            print(data)

        else:
            return redirect(url_for("creators_bp.my_contents"))

        return render_template("edit_movie.html", data=data)
    
    return redirect(url_for("auth.login"))

@creators_bp.route("/upload", methods=["GET", "POST"])
@cross_origin()
def upload_page():
    app.logger.info("Access Upload Page.")
    if current_user.is_authenticated:
        return render_template("upload_select.html")
    return redirect(url_for("auth.login"))


@creators_bp.route("/upload/movie", methods=["GET", "POST"])
def upload_movie():
    if current_user.is_authenticated:
        if request.method == "POST":
            thumbnail = request.files["thum"]
            sample = request.form.getlist("sample")
            sample = [url for url in sample if url.strip()]

            sample = [mID.split("?v=")[1][:11] for mID in sample] 

            extension = thumbnail.filename.split(".")[-1]
            random_name = uuid4().hex
            thumbnail_name = secure_filename(random_name)+"."+extension

            title = request.form.get("title")
            tags = request.form.get("tags")
            description = request.form.get("description")
            price = int(request.form.get("price"))

            basepath = os.path.join(app.config['MOVIE_FOLDER'])

            if request.form.get("content"):
                fullmovie = request.files["full"]
                extension = fullmovie.filename.split(".")[-1]
                random_name = uuid4().hex
                fullmovie_name = secure_filename(random_name)+"."+extension

                opath = os.path.join(basepath, "original", fullmovie_name)
        
                fullmovie.save(opath)
                GoogleDriveClass().upload(fullmovie_name)
            else:
                fullmovie_name = None

            ppath = os.path.join(basepath, "preview", thumbnail_name)
            thumbnail.save(ppath)

            category_id = Category.query.filter_by(name=tags).first().id

            if request.form.get("content"):
                new_movie = Movie(
                    title = title,
                    userid = current_user.id,
                    favorite = 0,
                    description = description,
                    price = price,
                    filename = fullmovie_name,
                    category_id = category_id
                )
            else:
                new_movie = Movie(
                    title = title,
                    userid = current_user.id,
                    favorite = 0,
                    description = description,
                    req_price = price,
                    filename = fullmovie_name,
                    category_id = category_id
                )

            db.session.add(new_movie)
            db.session.commit()

            

            thum = Thumbnail(
                movie_id = new_movie.id,
                filename = thumbnail_name
            )
            db.session.add(thum)
            db.session.commit()

            for mID in sample:
                mid = SampleLinks(
                    movie_id = new_movie.id,
                    url_link = mID
                )
                db.session.add(mid)
                db.session.commit()

            print("Add Movie...!")

        return render_template("upload_movie.html")
    return redirect(url_for("auth.login"))
            

@creators_bp.route("/upload/illust")
def upload_illust():
    if current_user.is_authenticated:
        return render_template("upload_illust.html")
    else:
        return redirect(url_for("auth.login"))