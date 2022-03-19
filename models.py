from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, current_user

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


class FavoriteMovie(db.Model):
	__table_name = 'favorite_movies'

	row_num = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, nullable=False)
	title = db.Column(db.String(80), nullable=False)
	movie_id = db.Column(db.Integer, nullable=False)


# stores the user id during session
@login.user_loader
def load_user(id):
	return UserModel.query.get(int(id))
