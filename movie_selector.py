import csv
import random
from datetime import datetime


movie_dict = {}
with open("static/disney_data.csv") as data:
    data_reader = csv.reader(data)
    next(data_reader)
    for line in list(data_reader):
        new_year = int(line[1])
        movie_dict[line[0]] = {'title': line[0],
                               'year released': new_year,
                               'studio': line[2],
                               'type': line[3],
                               'category': line[4],
                               'phase': line[5]}


def new_search(studio, year):
    """searches through dict for matching studio and year, creates list of
        both then randomizes and picks one to return"""
    list1 = []
    list2 = []
    for movie in movie_dict:
        if movie_dict[movie]['studio'] == studio or studio == 'No Preference':
            list1.append(movie)
            if year == 'Pre-1980s':
                if movie_dict[movie]['year released'] < 1980:
                    list2.append(movie)
            elif year == '1980-1999':
                if 1980 <= movie_dict[movie]['year released'] < 2000:
                    list2.append(movie)
            elif year == '2000-Today':
                if movie_dict[movie]['year released'] > 1999:
                    list2.append(movie)
            elif year == 'No Preference':
                list2.append(movie)
    new_set = set(list1) & set(list2)
    new_set_list = list(new_set)
    random_index = random.randint(0,len(new_set_list)-1)
    selected_movie = new_set_list[random_index]
    return selected_movie


def dis_countdown():
    """Countdown till disney from today - need to adjust for timezone"""
    today = datetime.today().date()
    disney_date = datetime(2022, 10, 9).date()
    delta = disney_date - today
    return delta.days

