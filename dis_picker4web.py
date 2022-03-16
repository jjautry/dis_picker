import sqlite3

from flask import Flask, render_template, request, redirect, session
from flask_login import login_required, current_user, login_user, logout_user
from movie_selector import dis_countdown
from models import DBConnect, db, login, UserModel, UserMoviesDB

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
    cursor = DBConnect().cursor
    cursor.execute("""SELECT *
                    FROM movies
                    ORDER BY RANDOM()
                    LIMIT 1;""")
    result = cursor.fetchall()
    return render_template("movie.html", result=result)


@app.route("/my_page")
@login_required
def my_page():

    return render_template("userpage.html")

@app.route("/preference")
@login_required
def preference():
    con = UserMoviesDB().connection
    cur = con.cursor()
    id = current_user.id
    cur.execute(f"SELECT title FROM user_dislike WHERE user_id={id};")
    result = cur.fetchall()
    return render_template("preference.html", result=result)


@app.route("/countdown")
def countdown():
    days = dis_countdown()
    return render_template("countdown.html", temp_days=days)


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


@app.route("/studio")
def studio():
    return render_template("studio.html")


@app.route("/marvel-phase")
def marvel():
    query = "SELECT * FROM movies WHERE production_company='Marvel' AND phase=1 ORDER BY RANDOM() LIMIT 1;"
    return render_template("marvel_phase.html")


@app.route("/studio/<studio>", methods=['POST', 'GET'])
def year(studio):

    if current_user.is_authenticated:
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
        cursor.close()
        string_result = str(result[0][0])

        query = "SELECT COUNT(*) FROM user_dislike WHERE user_id="+ str(current_user.id) + " AND title='" + string_result + "' ;"
        check_cur = UserMoviesDB().cursor
        check_cur.execute(query)
        result2 = check_cur.fetchall()
        if result2[0][0] > 0:
            year(studio)
        return render_template("movie.html", result=result)

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


@app.route("/movie")
def movie():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Dislike':
            return redirect('/countdown')
        elif request.form['submit_button'] == 'Favorite':
            pass
    elif request.method == 'GET':
        return render_template("movie.html", form=form)




if __name__ == '__main__':
    app.run(debug=True)
