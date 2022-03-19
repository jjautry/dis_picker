import sqlite3

from flask import Flask, render_template, request, redirect, session
from flask_login import login_required, current_user, login_user, logout_user
from movie_selector import dis_countdown
from models import DBConnect, db, login, UserModel, DislikeMovie, MovieDB

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
    return render_template('index.html')


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


@app.route('/random-movie')
def random_movie():
    result = db.engine.execute("SELECT * FROM movies ORDER BY RANDOM() LIMIT 1;")
    for movie in result:
        new_result = movie.id
    return redirect('/movie/'+ str(new_result))


@app.route("/my_page")
@login_required
def my_page():
    return render_template("userpage.html")

@app.route("/preference")
@login_required
def preference():
    id = current_user.id
    result = DislikeMovie.query.filter_by(user_id=id).all()
    return render_template("preference.html", result=result)


@app.route("/countdown")
def countdown():
    days = dis_countdown()
    return render_template("countdown.html", temp_days=days)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route("/studio", methods=['POST', 'GET'])
def studio():
    if request.method == 'POST':
        if request.form['studio_select'] == 'Disney':
            result = db.engine.execute("SELECT * FROM movies WHERE studio='Disney' ORDER BY RANDOM() LIMIT 1;")
            for movie in result:
                new_result = movie.id
            return redirect('/movie/' + str(new_result))

        elif request.form['studio_select'] == 'Pixar':
            result = db.engine.execute("SELECT * FROM movies WHERE studio='Pixar' ORDER BY RANDOM() LIMIT 1;")
            for movie in result:
                new_result = movie.id
            return redirect('/movie/' + str(new_result))

        elif request.form['studio_select'] == 'Lucasfilm':
            result = db.engine.execute("SELECT * FROM movies WHERE studio='Lucasfilm' ORDER BY RANDOM() LIMIT 1;")
            for movie in result:
                new_result = movie.id
            return redirect('/movie/' + str(new_result))

        elif request.form['studio_select'] == 'Marvel':
            result = db.engine.execute("SELECT * FROM movies WHERE studio='Marvel' ORDER BY RANDOM() LIMIT 1;")
            for movie in result:
                new_result = movie.id
            return redirect('/movie/' + str(new_result))

        elif request.form['studio_select'] == 'Disney Channel':
            result = db.engine.execute("SELECT * FROM movies WHERE studio='Disney Channel' ORDER BY RANDOM() LIMIT 1;")
            for movie in result:
                new_result = movie.id
            return redirect('/movie/' + str(new_result))

    return render_template("studio.html")


@app.route("/studio/<studio>", methods=['POST', 'GET'])
def year(studio):
    new_studio = str(studio)
    if new_studio == 'Lucasfilm':
        query = "SELECT * FROM movies WHERE production_company='Lucasfilm' ORDER BY RANDOM() LIMIT 1;"
    elif new_studio == 'Disney':
        query = "SELECT * FROM movies WHERE production_company='Disney' ORDER BY RANDOM() LIMIT 1;"
    elif new_studio == 'Disney Channel':
        query = "SELECT * FROM movies WHERE production_company='Disney Channel' ORDER BY RANDOM() LIMIT 1;"
    elif new_studio == 'Pixar':
        query = "SELECT * FROM movies WHERE production_company='Pixar' ORDER BY RANDOM() LIMIT 1;"
    elif new_studio == 'Marvel':
        query = "SELECT * FROM movies WHERE production_company='Marvel' ORDER BY RANDOM() LIMIT 1;"
    cursor = DBConnect().cursor
    cursor.execute(query)
    result = cursor.fetchall()
    return render_template("movie.html", result=result)


@app.route("/movie/<movie_id>", methods=['GET','POST'])
def movie(movie_id):
    """Checks if """
    if request.method == 'POST':
        if request.form['submit_button'] == 'Dislike':
            return redirect('/countdown')
        elif request.form['submit_button'] == 'Favorite':
            return redirect('/countdown')
    elif request.method == 'GET':
        result = MovieDB.query.filter_by(id=movie_id).first()
        return render_template("movie.html", result=result)



if __name__ == '__main__':
    app.run(debug=True)
