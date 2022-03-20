from flask import Flask, render_template, request, redirect, session, flash, get_flashed_messages
from flask_login import login_required, current_user, login_user, logout_user
from movie_selector import dis_countdown
from models import  db, login, UserModel, DislikeMovie, MovieDB, FavoriteMovie

app = Flask(__name__)
app.secret_key = 'slinkydogdash'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = False

db.init_app(app)
login.init_app(app)
login.login_view = 'login'


@app.before_first_request
def create_table():
    db.create_all()


@app.route('/')
def index():
    return render_template('index-2.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/my_page')

    if request.method == 'POST':
        username = request.form['username']
        user = UserModel.query.filter_by(username=username).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/my_page')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/my_page')

    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if UserModel.query.filter_by(email=email).first():
            return('Email already in use')
        elif UserModel.query.filter_by(username=username).first():
            return('Username already in use')

        user = UserModel(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')


@app.route("/my_page")
@login_required
def my_page():
    return render_template("userpage.html")


@app.route("/preference")
@login_required
def preference():
    id = current_user.id
    dislike = DislikeMovie.query.filter_by(user_id=id).all()
    favorite = FavoriteMovie.query.filter_by(user_id=id).all()
    return render_template("preference.html", dislike=dislike, favorite=favorite)


@app.route("/restore/<movie_id>")
@login_required
def restore(movie_id):
    db.engine.execute(f"DELETE FROM disliked_movies WHERE user_id ={current_user.id} AND movie_id={movie_id};")
    return redirect("/preference")


@app.route("/remove/<movie_id>")
@login_required
def remove(movie_id):
    db.engine.execute(f"DELETE FROM favorite_movie "
                      f"WHERE user_id ={current_user.id} "
                      f"AND movie_id={movie_id};")
    return redirect("/preference")


@app.route("/countdown")
def countdown():
    days = dis_countdown()
    return render_template("countdown.html", temp_days=days)


@app.route('/logout')
def logout():
    logout_user()
    flash("You have been logged out!", "info")
    return redirect('/')


@app.route('/random-movie')
def random_movie():
    result = db.engine.execute("SELECT * FROM movies ORDER BY RANDOM() LIMIT 1;")
    for movie in result:
        new_result = movie.id
    return redirect('/movie/'+ str(new_result))


@app.route("/studio", methods=['POST', 'GET'])
def studio():
    if request.method == 'POST':
        result = db.engine.execute(f"SELECT * FROM movies WHERE studio='{request.form['studio_select']}' "
                                   f"ORDER BY RANDOM() LIMIT 1;")
        for line in result:
            new_result = line.id
        return redirect('/movie/' + str(new_result))

    return render_template("studio.html")


@app.route("/movie/<movie_id>", methods=['GET','POST'])
def movie(movie_id):
    result = MovieDB.query.filter_by(id=movie_id).first()

    if request.method == 'POST':
        if current_user.is_authenticated:
            if request.form['submit_button'] == 'Dislike':
                reject = DislikeMovie(user_id=current_user.id, title=result.title, movie_id=result.id)
                db.session.add(reject)
                db.session.commit()
                return redirect("/studio")
            elif request.form['submit_button'] == 'Favorite':
                fav = FavoriteMovie(user_id=current_user.id, title=result.title, movie_id=result.id)
                db.session.add(fav)
                db.session.commit()
                return redirect('/studio')

    return render_template("movie.html", result=result)


if __name__ == '__main__':
    app.run(debug=True)
