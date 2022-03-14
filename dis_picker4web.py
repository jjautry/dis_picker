from flask import Flask, render_template, request, flash, redirect, session
from movie_selector import dis_countdown
from models import DBConnect

app = Flask(__name__)
app.config['SECRET KEY'] = 'slinkydogdash'


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')






def get_studio():
    """Returns all distinct studios in a list"""
    cur = DBConnect().cursor
    cur.execute("SELECT DISTINCT studio FROM movies;")
    studio_list = []
    for studio in cur.fetchall():
        studio_list.append(studio[0])
    return sorted(studio_list)




@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/countdown")
def countdown():
    days = dis_countdown()
    return render_template("countdown.html", temp_days=days)




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
