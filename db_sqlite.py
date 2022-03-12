import sqlite3
from movie_selector import movie_dict

# Create and connect to dis-movies.db
connection = sqlite3.connect("data/dis-movies.db")
cursor = connection.cursor()

# Create table for movies
# cursor.execute("""CREATE TABLE movies
# 				(title TEXT, year INTEGER, studio TEXT, category TEXT,
# 				type TEXT, phase INTEGER);""")

#Dict of movies -> sqlite db
for movie in movie_dict:
	title = movie_dict[movie]['title']
	year = movie_dict[movie]['year released']
	studio = movie_dict[movie]['studio']
	category = movie_dict[movie]['category']
	type = movie_dict[movie]['type']
	phase = movie_dict[movie]['phase']
	cursor.execute("""INSERT INTO movies 
	VALUES (?,?,?,?,?,?)""", (title, year, studio, category, type, phase))

connection.commit()

cursor.execute("SELECT * FROM movies;")
print(cursor.fetchall())