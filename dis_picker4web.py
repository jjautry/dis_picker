from flask import Flask, render_template, request, flash, redirect
from movie_selector import new_search, movie_dict, dis_countdown

app = Flask(__name__)
app.config['SECRET KEY'] = 'slinkydogdash'

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        studio = request.form["studio"]
        year = request.form["time period"]
        if studio == "Pick a studio:" or year == "Time period:":
            pass
        else:
            try:
                temp_movie = new_search(studio, year)
                movie_url = "/movie/" + str(temp_movie)
                return redirect(movie_url)
            except:
                pass
    return render_template('index.html')


@app.route('/movie/<movie_name>')
def movie(movie_name):
    if movie_name in movie_dict:
        name = movie_dict[movie_name]['title']
        studio = movie_dict[movie_name]['studio']
        year = movie_dict[movie_name]['year released']
        category = movie_dict[movie_name]['category']
        logo_url = ""
        if studio == "Disney":
            logo_url = "../static/The_Walt_Disney_Studios_logo.png"
        elif studio == "Disney Channel":
            logo_url = "../static/disneychannel.png"
        elif studio == "Marvel":
            logo_url = "../static/marvel.png"
        elif studio == "Pixar":
            logo_url = "../static/pixar.png"
        elif studio == "Lucasfilm":
            logo_url = "../static/lucasfilm.png"

    return render_template('movie.html', temp_name=name,
                           temp_studio=studio, temp_year=year,
                           temp_cat = category, temp_logo_url=logo_url)

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/countdown")
def countdown():
    days = dis_countdown()
    return render_template("countdown.html", temp_days=days)



if __name__ == '__main__':
    app.run(debug=True)
