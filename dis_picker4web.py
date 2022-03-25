from flask import Flask, render_template, request, redirect, session, flash
from flask_login import login_required, current_user, login_user, logout_user
from models import db, login, UserModel, DislikeMovie, MovieDB, FavoriteMovie, FeedbackDB, dis_countdown
from datetime import datetime
import random
import time

app = Flask(__name__)
app.secret_key = 'slinkydogdash'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_NOTIFICATIONS'] = False

db.init_app(app)
login.init_app(app)
login.login_view = 'login'

# if no tables are in databases, create them
@app.before_first_request
def create_table():
	db.create_all()


@app.route('/')
def index():
	return render_template('index-2.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
	if current_user.is_authenticated:
		return redirect('/user_page')

	if request.method == 'POST':
		username = request.form['username']
		user = UserModel.query.filter_by(username=username).first()
		if user is not None and user.check_password(request.form['password']):
			login_user(user)
			user.num_logins += 1
			user.last_login = datetime.today().date()
			db.session.commit()
			return redirect('/user_page')

	return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
	if current_user.is_authenticated:
		return redirect('/user_page')

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


@app.route("/user_page")
@login_required
def my_page():
	return redirect("/user_page/likes")


@app.route("/user_page/likes")
@login_required
def likes():
	id = current_user.id
	favorite = FavoriteMovie.query.filter_by(user_id=id).all()
	return render_template("userpage_likes.html", favorite=favorite)


@app.route("/user_page/dislikes")
@login_required
def dislikes():
	id = current_user.id
	dislike = DislikeMovie.query.filter_by(user_id=id).all()
	return render_template("userpage_dislikes.html", dislike=dislike)


@app.route("/user_page/countdown", methods=["POST", "GET"])
@login_required
def countdown():
	id = current_user.id
	if request.method == "POST":
		user = UserModel.query.filter_by(id=id).first()
		date = datetime.strptime(request.form['disney_date'], '%Y-%m-%d').date()
		user.disney_date = date
		db.session.commit()
		return redirect("/user_page/countdown")

	user = UserModel.query.filter_by(id=id).first()
	if user.disney_date:
		days = dis_countdown(user.disney_date)
	else:
		days = 0

	return render_template("userpage_countdown.html", days=days)


@app.route("/remove-dis-date")
@login_required
def remove_dis_date():
	id = current_user.id
	user = UserModel.query.filter_by(id=id).first()
	user.disney_date = None
	db.session.commit()
	return redirect("/user_page/countdown")



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
	return redirect("/user_page/dislikes")


@app.route("/remove/<movie_id>")
@login_required
def remove(movie_id):
	db.engine.execute(f"DELETE FROM favorite_movie "
					  f"WHERE user_id ={current_user.id} "
					  f"AND movie_id={movie_id};")
	return redirect("/user_page/likes")


@app.route('/logout')
def logout():
	logout_user()
	return redirect('/')


@app.route('/random-movie')
def random_movie():
	result = db.engine.execute("SELECT * FROM movies ORDER BY RANDOM() LIMIT 1;")
	if current_user.is_authenticated:
		for line in result:
			new_result = line.id
			check = DislikeMovie().check_in(current_user.id, new_result)
			if check:
				return studio()
			else:
				pass
	for movie in result:
		new_result = movie.id
	return redirect('/movie/'+ str(new_result))


@app.route("/studio", methods=['POST', 'GET'])
def studio():
	if request.method == 'POST':
		result = db.engine.execute(f"SELECT * FROM movies WHERE studio='{request.form['studio_select']}' "
								   f"ORDER BY RANDOM() LIMIT 1;")
		if current_user.is_authenticated:
			for line in result:
				new_result = line.id
				check = DislikeMovie().check_in(current_user.id, new_result)
				if check:
					return studio()
				else:
					pass
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
				return redirect('/user_page/likes')

	return render_template("movie.html", result=result, id=movie_id)


@app.route("/random-faves/<user_id>")
def random_fav(user_id):
	id = user_id
	faves = []
	result = FavoriteMovie.query.filter_by(user_id=id).all()
	for movie in result:
		faves.append(movie.movie_id)
	if len(faves) < 1:
		return "<h1>You don't have any favorites!</h1>"
	else:
		choice = random.choice(faves)
		return redirect("/movie/"+str(choice))


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


@app.route('/admin')
@login_required
def admin():
	if current_user.id == 1:
		users = UserModel.query.all()
		feedback = FeedbackDB.query.all()
		user_count = UserModel.query.count()
		feedback_count = FeedbackDB.query.count()
		return render_template("admin.html", users=users, feedback=feedback, user_count=user_count, feedback_count=feedback_count)
	else:
		return redirect("/")


@app.route('/feedback')
@app.route('/missing-poster/<movie_id>')
def feedback(movie_id=None):
	if movie_id:
		id = current_user.id
		missing_msg = "Missing Poster for movie #" + movie_id
		date = datetime.today().date()
		fb = FeedbackDB(user_id=id, message=missing_msg, date=date)
		db.session.add(fb)
		db.session.commit()
	return redirect("/#movie-options")

@app.route('/remove/feedback/<id>')
def remove_feedback(id):
	db.engine.execute(f"DELETE FROM feedback WHERE id ={id};")

	return redirect("/admin")


if __name__ == '__main__':
	app.run(debug=True)
