from flask import Flask, render_template, request, redirect, send_from_directory
from flask_login import login_required, current_user, login_user, logout_user
from models import db, login, UserModel, DislikeMovie, MovieDB, FavoriteMovie, FeedbackDB, \
    dis_countdown, AttractionDB, UserAttractionDB, MovieSelectionDB
from datetime import datetime
import random
from math import floor
from sqlalchemy.sql.expression import func

app = Flask(__name__)
app.secret_key = 'slinkydogdash'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login.init_app(app)
login.login_view = 'login'


# if no tables are in databases, create them
@app.before_first_request
def create_table():
    db.create_all()


# homepage
@app.route('/')
def index():
    return render_template('index-2.html')


# login page
@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/user-page')

    if request.method == 'POST':
        username = request.form['username']
        user = UserModel.query.filter_by(username=username).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            user.num_logins += 1
            user.last_login = datetime.today().date()
            db.session.commit()
            return redirect('/user-page')

    return render_template('login.html')


# register page
@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/user-page')

    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if UserModel.query.filter_by(email=email).first():
            return 'Email already in use'
        elif UserModel.query.filter_by(username=username).first():
            return 'Username already in use'

        user = UserModel(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user)
        user.num_logins += 1
        user.last_login = datetime.today().date()
        db.session.commit()

        new_account = True
        return render_template("userpage_likes.html", newAccount=new_account)

    return render_template('register.html')


# user page -> redirects to likes
@app.route("/user-page")
@login_required
def my_page():
    return redirect("/user-page/likes")


# user's liked movies
@app.route("/user-page/likes")
@login_required
def likes():
    id = current_user.id
    favorite = FavoriteMovie.query.filter_by(user_id=id).order_by(FavoriteMovie.title).all()
    return render_template("userpage_likes.html", favorite=favorite)


# user's disliked movies
@app.route("/user-page/dislikes")
@login_required
def dislikes():
    id = current_user.id
    dislike = DislikeMovie.query.filter_by(user_id=id).order_by(DislikeMovie.title).all()
    return render_template("userpage_dislikes.html", dislike=dislike)


# user's disney trip countdown
@app.route("/user-page/countdown", methods=["POST", "GET"])
@login_required
def countdown():
    id = current_user.id
    if request.method == "POST":
        user = UserModel.query.filter_by(id=id).first()
        date = datetime.strptime(request.form['disney_date'], '%Y-%m-%d').date()
        user.disney_date = date
        db.session.commit()
        return redirect("/countdown")

    user = UserModel.query.filter_by(id=id).first()
    if user.disney_date:
        days = dis_countdown(user.disney_date)
    else:
        days = 0
    return render_template("countdown.html", days=days)


# disney trip countdown
@app.route("/countdown", methods=["POST", "GET"])
def countdown_v2():
    if current_user.is_authenticated:
        user = UserModel.query.filter_by(id=current_user.id).first()
        if request.method == "POST":
            date = datetime.strptime(request.form['disney_date'], '%Y-%m-%d').date()
            user.disney_date = date
            db.session.commit()
            return redirect("/countdown")

        if user.disney_date:
            days = dis_countdown(user.disney_date)
        else:
            days = 0
        return render_template("countdown.html", days=days)

    else:
        if request.method == "POST":
            user_date = datetime.strptime(request.form['disney_date'], '%Y-%m-%d').date()
            days = dis_countdown(user_date)
            if days < 0:
                days = 0
            return render_template("countdown.html", days=days)

    return render_template("countdown.html")


# remove user's disney trip date
@app.route("/remove-dis-date")
@login_required
def remove_dis_date():
    id = current_user.id
    user = UserModel.query.filter_by(id=id).first()
    user.disney_date = None
    db.session.commit()
    return redirect("/countdown")


# take movie out of user's disliked
@app.route("/restore/<movie_id>")
@login_required
def restore(movie_id):
    db.engine.execute(f"DELETE FROM disliked_movies WHERE user_id ={current_user.id} AND movie_id={movie_id};")
    return redirect("/user-page/dislikes")


# take movie out of user's liked
@app.route("/remove/<movie_id>")
@login_required
def remove(movie_id):
    db.engine.execute(f"DELETE FROM favorite_movie "
                      f"WHERE user_id ={current_user.id} "
                      f"AND movie_id={movie_id};")
    return redirect("/user-page/likes")


# logout -> redirects to homepage
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


# function to give random movie
@app.route('/random-movie', methods=['POST', 'GET'])
def random_movie():
    result = MovieDB.query.filter(MovieDB.studio!='Disney Channel').order_by(func.random()).first()
    #for count in result:
    #    return redirect('/movie/' + str(count.count))
    return redirect('/movie/' + str(result.id))


# random movie from chosen studio
@app.route("/studio", methods=['POST', 'GET'])
def studio(name=None):
    if request.method == 'POST':
        result = MovieDB.query.filter_by(studio=request.form['studio_select']).order_by(func.random()).first()
        if current_user.is_authenticated:
            result_log = MovieSelectionDB(date=datetime.today().date(), user_id=current_user.id, studio_selection=result.studio, movie_result_id=result.id)
            db.session.add(result_log)
            db.session.commit()
            return redirect('/movie/' + str(result.id))
        else:
            result_log = MovieSelectionDB(date=datetime.today().date(), user_id=None, studio_selection=result.studio, movie_result_id=result.id)
            db.session.add(result_log)
            db.session.commit()
            return redirect('/movie/' + str(result.id))

    return render_template("studio.html")


# movie page
@app.route("/movie/<movie_id>", methods=['GET', 'POST'])
def movie(movie_id):
    result = MovieDB.query.filter_by(id=movie_id).first()

    if current_user.is_authenticated:
        fav_check = False
        check = FavoriteMovie().check_in(current_user.id, result.id)
        if check:
            fav_check = True
        else:
            fav_check = False
        return render_template("movie.html", result=result, id=movie_id, fav_check=fav_check)

    if request.method == 'POST':
        # Dislike button
        if request.form['submit_button'] == 'Dislike':
            reject = DislikeMovie(user_id=current_user.id, title=result.title, movie_id=result.id)
            db.session.add(reject)
            db.session.commit()
            return redirect("/studio")
        # Favorite button
        elif request.form['submit_button'] == 'Favorite':
            fav = FavoriteMovie(user_id=current_user.id, title=result.title, movie_id=result.id)
            db.session.add(fav)
            db.session.commit()
            return redirect('/user-page/likes')


    return render_template("movie.html", result=result, id=movie_id)


# random movie from user favorites
@app.route("/random-faves/<user_id>")
def random_fav(user_id):
    id = user_id
    faves = []
    result = FavoriteMovie.query.filter_by(user_id=id).all()
    for movie in result:
        faves.append(movie.movie_id)
    if len(faves) < 1:
        noFavorites = True
        return render_template("userpage_likes.html", noFavorites=noFavorites)
    else:
        choice = random.choice(faves)
        return redirect("/movie/" + str(choice))


# about me page
@app.route("/about", methods=['POST', 'GET'])
def about():
    if request.method == 'POST':
        if current_user.is_authenticated:
            user_id = current_user.id
            message = request.form['feedback']
            date = datetime.today().date()
            fb = FeedbackDB(user_id=user_id, message=message, date=date)
            db.session.add(fb)
            db.session.commit()
        else:
            user_id = 11420690
            message = request.form['feedback']
            date = datetime.today().date()
            fb = FeedbackDB(user_id=user_id, message=message, date=date)
            db.session.add(fb)
            db.session.commit()

    return render_template("about.html")


# admin page
@app.route('/admin')
@login_required
def admin():
    if current_user.id == 1:
        users = UserModel.query.all()
        feedback = FeedbackDB.query.all()
        user_count = UserModel.query.count()
        feedback_count = FeedbackDB.query.count()
        return render_template("admin.html", users=users, feedback=feedback, user_count=user_count,
                               feedback_count=feedback_count)
    else:
        return redirect("/")


# remove feedback
@app.route('/remove/feedback/<id>')
def remove_feedback(id):

    db.engine.execute(f"DELETE FROM feedback WHERE id ={id};")

    return redirect("/admin")


# user bucket list page
@app.route('/bucket-list')
def bucket_list():
    attractions = AttractionDB.query.all()
    # park totals
    wdw_total = AttractionDB.query.count()
    mk_total = AttractionDB.query.filter_by(park="Magic Kingdom").count()
    hs_total = AttractionDB.query.filter_by(park="Hollywood Studios").count()
    ep_total = AttractionDB.query.filter_by(park="Epcot").count()
    ak_total = AttractionDB.query.filter_by(park="Animal Kingdom").count()

    if current_user.is_authenticated:
        """Queries all counts of attractions in parks and user ridden"""
        id = current_user.id
        # user totals
        user_total = UserAttractionDB.query.filter_by(user_id=id).count()
        mk_user = UserAttractionDB.query.filter_by(user_id=id, park="Magic Kingdom").count()
        hs_user = UserAttractionDB.query.filter_by(user_id=id, park="Hollywood Studios").count()
        ep_user = UserAttractionDB.query.filter_by(user_id=id, park="Epcot").count()
        ak_user = UserAttractionDB.query.filter_by(user_id=id, park="Animal Kingdom").count()
        user_lst = []
        for ride in UserAttractionDB.query.filter_by(user_id=id).all():
            user_lst.append(ride.attraction_id)

        percent = floor((user_total / wdw_total) * 100)
        return render_template("bucket-landing.html", attractions=attractions, mk_total=mk_total,
                               mk_user=mk_user, hs_user=hs_user, hs_total=hs_total, ep_user=ep_user,
                               ep_total=ep_total, ak_user=ak_user, ak_total=ak_total, user_total=user_total,
                               wdw_total=wdw_total, user_lst=user_lst, percent=percent)

    return render_template("bucket-landing.html", attractions=attractions, wdw_total=wdw_total, mk_total=mk_total,
                           hs_total=hs_total, ep_total=ep_total, ak_total=ak_total)


# add attraction to user profile
@app.route('/add-attraction/<park>/<id>')
@login_required
def add_attraction(id, park):
    user_id = current_user.id
    att_info = AttractionDB.query.filter_by(id=id).first()
    user_att = UserAttractionDB(user_id=user_id, attraction_id=id, park=att_info.park, land=att_info.land,
                                attraction=att_info.attraction)
    db.session.add(user_att)
    db.session.commit()

    return redirect(f"/bucket-list/{park}#ride-selection")


# remove attraction from user profile
@app.route('/remove-attraction/<park>/<id>')
@login_required
def remove_attraction(id, park):
    db.engine.execute(f"DELETE FROM user_attractionDB "
                      f"WHERE user_id ={current_user.id} "
                      f"AND attraction_id={id};")
    return redirect(f"/bucket-list/{park}#ride-selection")


# bucket list park page
@app.route('/bucket-list/<park>')
def bucket_list_park(park):
    attractions = AttractionDB.query.filter_by(park=park).order_by(AttractionDB.land, AttractionDB.attraction).all()
    attraction_count = AttractionDB.query.filter_by(park=park).count()

    image = ""
    if park == "Magic Kingdom":
        image = "/static/mk_logo.png"
    elif park == "Epcot":
        image = "/static/epcot_logo.webp"
    elif park == "Hollywood Studios":
        image = "/static/hs_logo.gif"
    else:
        image = "/static/ak_logo.webp"

    if current_user.is_authenticated:
        user_count = UserAttractionDB.query.filter_by(park=park, user_id=current_user.id).count()

        user_lst = []
        for ride in UserAttractionDB.query.filter_by(user_id=current_user.id).all():
            user_lst.append(ride.attraction_id)

        return render_template("park.html", image=image, park=park, attractions=attractions,
                               attraction_count=attraction_count, user_count=user_count, user_lst=user_lst)

    return render_template("park.html", image=image, park=park, attractions=attractions,
                           attraction_count=attraction_count)



@app.route('/maintenance')
def maintenance():
    return render_template("construction.html")


@app.route('/policy.html')
@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == '__main__':
    app.run(debug=True)
