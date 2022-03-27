from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, current_user
from datetime import datetime

# using LoginManager
login = LoginManager()
db = SQLAlchemy()


# SQLAlchemy models
# creates db model and connects with user data
class UserModel(UserMixin, db.Model):
	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(80), unique=True)
	username = db.Column(db.String(100), unique=True)
	password_hash = db.Column(db.String())
	disney_date = db.Column(db.Date())
	num_logins = db.Column(db.Integer, default=0)
	last_login = db.Column(db.Date())

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)


# movie table
class MovieDB(db.Model):
	__tablename__ = 'movies'

	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String, nullable=False)
	year = db.Column(db.Integer, nullable=False)
	studio = db.Column(db.String, nullable=False)
	category = db.Column(db.String, nullable=False)
	type = db.Column(db.String, nullable=False)
	phase = db.Column(db.Integer)
	poster = db.Column(db.String, nullable=False)


# user's disliked movies
class DislikeMovie(db.Model):
	__tablename__ = 'disliked_movies'

	row_num = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, nullable=False)
	title = db.Column(db.String(80), nullable=False)
	movie_id = db.Column(db.Integer, nullable=False)

	def check_in(self, user_id, movie_id):
		"""Checks if user_id and movie_id have a match in disliked movies"""
		usr_lst = []
		result = DislikeMovie.query.filter_by(user_id=user_id)
		for movie in result:
			usr_lst.append(movie.movie_id)
		if movie_id in usr_lst:
			return True
		else:
			return False


# user's favorite movies
class FavoriteMovie(db.Model):
	__tablename__ = 'favorite_movie'

	row_num = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, nullable=False)
	title = db.Column(db.String(80), nullable=False)
	movie_id = db.Column(db.Integer, nullable=False)


# user feedback from about page
class FeedbackDB(db.Model):
	__tablename__ = 'feedback'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, nullable=False)
	message = db.Column(db.String, nullable=False)
	date = db.Column(db.Date())


# disney world attraction table
class AttractionDB(db.Model):
	__tablename__ = 'attractions'

	id = db.Column(db.Integer, primary_key=True)
	park = db.Column(db.String, nullable=False)
	land = db.Column(db.String, nullable=False)
	attraction = db.Column(db.String, nullable=False)
	dis_link = db.Column(db.String)
	img = db.Column(db.String)


class UserAttractionDB(db.Model):
	__table_name = 'user_attraction'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, nullable=False)
	attraction_id = db.Column(db.Integer, nullable=False)
	park = db.Column(db.String, nullable=False)
	land = db.Column(db.String, nullable=False)
	attraction = db.Column(db.String, nullable=False)

	def check_in(self, user_id, attraction_id):
		"""Checks if user_id and attraction_id have a match in user attraction"""
		usr_lst = []
		result = UserAttractionDB.query.filter_by(user_id=user_id)
		for attraction in result:
			usr_lst.append(attraction.attraction.id)
		if attraction_id in usr_lst:
			return True
		else:
			return False

# stores the user id during session
@login.user_loader
def load_user(id):
	return UserModel.query.get(int(id))



def dis_countdown(disney_date):
    """Takes current date and returns days left until Disney trip"""
    today = datetime.today().date()
    delta = disney_date - today
    return delta.days
