from flask import Flask, render_template, request, redirect, session, flash
from flask_login import login_required, current_user, login_user, logout_user
from models import db, login, UserModel, DislikeMovie, MovieDB, FavoriteMovie, FeedbackDB, dis_countdown, AttractionDB, UserAttractionDB
from datetime import datetime
import random
from math import floor

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


# homepage
@app.route('/')
def index():
	return render_template('index-2.html')


# login page
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


#register page
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

		login_user(user)
		user.num_logins += 1
		user.last_login = datetime.today().date()
		db.session.commit()

		newAccount = True
		return render_template("userpage_likes.html", newAccount=newAccount)

	return render_template('register.html')


# user page -> redirects to likes
@app.route("/user_page")
@login_required
def my_page():
	return redirect("/user_page/likes")


# user's liked movies
@app.route("/user_page/likes")
@login_required
def likes():
	id = current_user.id
	favorite = FavoriteMovie.query.filter_by(user_id=id).all()
	return render_template("userpage_likes.html", favorite=favorite)


# user's disliked movies
@app.route("/user_page/dislikes")
@login_required
def dislikes():
	id = current_user.id
	dislike = DislikeMovie.query.filter_by(user_id=id).all()
	return render_template("userpage_dislikes.html", dislike=dislike)


# user's disney trip countdown
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


# removes user's disney trip date
@app.route("/remove-dis-date")
@login_required
def remove_dis_date():
	id = current_user.id
	user = UserModel.query.filter_by(id=id).first()
	user.disney_date = None
	db.session.commit()
	return redirect("/user_page/countdown")


# takes movie out of user's disliked
@app.route("/restore/<movie_id>")
@login_required
def restore(movie_id):
	db.engine.execute(f"DELETE FROM disliked_movies WHERE user_id ={current_user.id} AND movie_id={movie_id};")
	return redirect("/user_page/dislikes")


# takes movie out of user's liked
@app.route("/remove/<movie_id>")
@login_required
def remove(movie_id):
	db.engine.execute(f"DELETE FROM favorite_movie "
					  f"WHERE user_id ={current_user.id} "
					  f"AND movie_id={movie_id};")
	return redirect("/user_page/likes")


# logout -> redirects to homepage
@app.route('/logout')
def logout():
	logout_user()
	return redirect('/')


# function to give random movie
@app.route('/random-movie', methods=['POST','GET'])
def random_movie():
	result = db.engine.execute("SELECT * FROM movies ORDER BY RANDOM() LIMIT 1;")
	if current_user.is_authenticated:
		for line in result:
			new_result = line.id
			check = DislikeMovie().check_in(current_user.id, new_result)
			if check:
				return random_movie()
			else:
				pass
	for movie in result:
		new_result = movie.id
	return redirect('/movie/'+ str(new_result))


# random movie from chosen studio
@app.route("/studio", methods=['POST', 'GET'])
def studio(name=None):
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


# movie page
@app.route("/movie/<movie_id>", methods=['GET','POST'])
def movie(movie_id):
	result = MovieDB.query.filter_by(id=movie_id).first()

	if request.method == 'POST':
		if current_user.is_authenticated:
			if request.form['submit_button'] == 'Dislike':
				reject = DislikeMovie(user_id=current_user.id, title=result.title, movie_id=result.id)
				db.session.add(reject)
				db.session.commit()
				return redirect("/#movie-options")
			elif request.form['submit_button'] == 'Favorite':
				fav = FavoriteMovie(user_id=current_user.id, title=result.title, movie_id=result.id)
				db.session.add(fav)
				db.session.commit()
				return redirect('/user_page/likes')

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
		return redirect("/movie/"+str(choice))


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
		return render_template("admin.html", users=users, feedback=feedback, user_count=user_count, feedback_count=feedback_count)
	else:
		return redirect("/")


# sends feedback/missing poster message to fb data
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


# user bucket list page
@app.route('/user_page/bucket_list')
@login_required
def bucket_list():
	"""Queries all counts of attractions in parks and user ridden"""
	id = current_user.id
	attractions = AttractionDB.query.all()

	# user totals
	user_total = UserAttractionDB.query.filter_by(user_id=id).count()
	mk_user = UserAttractionDB.query.filter_by(park="Magic Kingdom", user_id=id).count()
	hs_user = UserAttractionDB.query.filter_by(park="Hollywood Studios", user_id=id).count()
	ep_user = UserAttractionDB.query.filter_by(park="Epcot", user_id=id).count()
	ak_user = UserAttractionDB.query.filter_by(park="Animal Kingdom", user_id=id).count()
	user_lst = []
	for ride in UserAttractionDB.query.filter_by(user_id=id).all():
		user_lst.append(ride.attraction_id)

	# park totals
	wdw_total = AttractionDB.query.count()
	mk_total = AttractionDB.query.filter_by(park="Magic Kingdom").count()
	hs_total = AttractionDB.query.filter_by(park="Hollywood Studios").count()
	ep_total = AttractionDB.query.filter_by(park="Epcot").count()
	ak_total = AttractionDB.query.filter_by(park="Animal Kingdom").count()

	percent = floor((user_total/wdw_total) * 100)

	return render_template("bucket-list.html", attractions=attractions, mk_total=mk_total,
						   mk_user=mk_user, hs_user=hs_user, hs_total=hs_total, ep_user=ep_user,
						   ep_total=ep_total, ak_user=ak_user, ak_total=ak_total, user_total=user_total,
						   wdw_total=wdw_total, user_lst=user_lst, percent=percent)


# add attraction to user profile
@app.route('/add-attraction/<park>/<id>')
@login_required
def add_attraction(id, park):
	user_id = current_user.id
	att_info = AttractionDB.query.filter_by(id=id).first()
	user_att = UserAttractionDB(user_id=user_id, attraction_id=id, park=att_info.park, land=att_info.land, attraction=att_info.attraction)
	db.session.add(user_att)
	db.session.commit()

	return redirect(f"/user_page/bucket_list/{park}#ride-selection")


# remove attraction from user profile
@app.route('/remove-attraction/<park>/<id>')
@login_required
def remove_attraction(id,park):
	db.engine.execute(f"DELETE FROM user_attractionDB "
					  f"WHERE user_id ={current_user.id} "
					  f"AND attraction_id={id};")
	return redirect(f"/user_page/bucket_list/{park}#ride-selection")


# bucket list park page
@app.route('/user_page/bucket_list/<park>')
@login_required
def bucket_list_park(park):
	attractions = AttractionDB.query.filter_by(park=park).all()
	attraction_count = AttractionDB.query.filter_by(park=park).count()
	user_count = UserAttractionDB.query.filter_by(park=park, user_id=current_user.id).count()

	user_lst = []
	for ride in UserAttractionDB.query.filter_by(user_id=current_user.id).all():
		user_lst.append(ride.attraction_id)

	image = ""
	land_lst = []
	if park == "Magic Kingdom":
		image = "/static/mk_logo.png"
	elif park == "Epcot":
		image = "/static/epcot_logo.webp"
	elif park == "Hollywood Studios":
		image = "/static/hs_logo.gif"
	else:
		image = "/static/ak_logo.webp"

	return render_template("park.html", image=image, park=park, attractions=attractions, attraction_count=attraction_count, user_count=user_count, user_lst=user_lst)


if __name__ == '__main__':
	app.run(debug=True)
