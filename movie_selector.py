import csv
import random

movie_dict = {}
with open('data/disney_data.csv') as data:
    """Converts dataset into dictionary movie_dict"""
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



def get_movie(studio, year):
    producers = ""
    time_period = ""
    if studio == 'Disney':
        producers = '1'
    elif studio == 'Pixar':
        producers = '2'
    elif studio == 'Lucas Films':
        producers = '3'
    else:
        producers = '4'

    if year == 'Pre-1980s':
        time_period = '1'
    elif year == '1980-1999':
        time_period = '2'
    elif year == '2000-Today':
        time_period = '3'
    else:
        time_period = '4'

    producer_sorted = {}
    for movie in movie_dict:
        if producers == '4':
            producer_sorted[movie] = movie_dict[movie]
        elif producers == '1':
            if movie_dict[movie]['studio'] == 'Disney':
                producer_sorted[movie] = movie_dict[movie]
            else:
                pass
        elif producers == '2':
            if movie_dict[movie]['studio'] == 'Pixar':
                producer_sorted[movie] = movie_dict[movie]
            else:
                pass
        elif producers == '3':
            if movie_dict[movie]['studio'] == 'Lucas Film':
                producer_sorted[movie] = movie_dict[movie]
            else:
                pass
        else:
            print('Invalid selection, try again.')

    random_list = []
    for movie in producer_sorted:
        if time_period == '1':
            if producer_sorted[movie]['year released'] < 1980:
                random_list.append(movie)
            else:
                pass
        elif time_period == '2':
            if producer_sorted[movie]['year released'] >= 1980 and producer_sorted[movie]['year released'] < 2000:
                random_list.append(movie)
            else:
                pass
        elif time_period == '3':
            if producer_sorted[movie]['year released'] >= 2000:
                random_list.append(movie)
            else:
                pass
        elif time_period == '4':
            random_list.append(movie)
        else:
            print('Invalid selection, try again.')

    random_index = random.randint(0,(len(random_list)-1))
    movie_choice = random_list[random_index]
    return movie_choice



