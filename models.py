from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, current_user
import sqlite3

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


class DislikeMovie(db.Model):
	__tablename__ = 'disliked_movies'

	row_num = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, nullable=False)
	title = db.Column(db.String(80), nullable=False)




class DBConnect:
	"""Class for SQLite db connection and search function"""
	def __init__(self):
		self.connection = sqlite3.connect("data/dis-movies.db")
		self.cursor = self.connection.cursor()

	def get_studio(self):
		"""Returns all distinct studios in a list"""
		self.cursor.execute("SELECT DISTINCT studio FROM movies;")
		studio_list = []
		for studio in self.cursor.fetchall():
			studio_list.append(studio[0])
		self.connection.close()
		return sorted(studio_list)


# userconn = sqlite3.connect("data/user_movies.db")
# usercur = userconn.cursor()
# moviecur = DBConnect().cursor
# moviecur.execute("SELECT title FROM movies WHERE production_company='Marvel';")
# result1 = moviecur.fetchall()
#
# with sqlite3.connect("data/user_movies.db") as con:
# 	for result in result1:
# 		title = result[0]
# 		user_id = 1
# 		usercur.execute("INSERT INTO user_dislike ('user_id', 'title') VALUES(?,?)", (user_id, title))
# 		userconn.commit()
#
# 	usercur.close()
# 	userconn.close()
# 	moviecur.close()




# stores the user id during session
@login.user_loader
def load_user(id):
	return UserModel.query.get(int(id))
