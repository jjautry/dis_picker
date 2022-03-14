from flask import Flask, render_template, request, redirect, session
from flask_login import login_required, current_user, login_user, logout_user
from movie_selector import dis_countdown
from models import DBConnect, db, login, UserModel

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




@app.route("/my_page")
@login_required
def my_page():
    return render_template("userpage.html")

@app.route("/countdown")
def countdown():
    days = dis_countdown()
    return render_template("countdown.html", temp_days=days)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')




# @app.route('/movie/<movie_name>')
# def movie(movie_name):
#     """This is outdated and will be deleted"""
#     if movie_name in movie_dict:
#         name = movie_dict[movie_name]['title']
#         studio = movie_dict[movie_name]['studio']
#         year = movie_dict[movie_name]['year released']
#         category = movie_dict[movie_name]['category']
#         logo_url = ""
#         if studio == "Disney":
#             logo_url = "../static/The_Walt_Disney_Studios_logo.png"
#         elif studio == "Disney Channel":
#             logo_url = "../static/disneychannel.png"
#         elif studio == "Marvel":
#             logo_url = "../static/marvel.png"
#         elif studio == "Pixar":
#             logo_url = "../static/pixar.png"
#         elif studio == "Lucasfilm":
#             logo_url = "../static/lucasfilm.png"
#
#     return render_template('movie.html', temp_name=name,
#                            temp_studio=studio, temp_year=year,
#                            temp_cat = category, temp_logo_url=logo_url)



if __name__ == '__main__':
    app.run(debug=True)
