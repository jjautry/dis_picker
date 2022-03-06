import csv
import random
from datetime import datetime


def movie_picker():
    provided_year = input("What is the oldest age movie you want to watch? (type year ex: 1994")
    new_year = datetime.strptime(provided_year + "/01/01", '%Y/%m/%d')
    time_delta = new_year - new_year
    movie_dict = {}

    with open('DisneyMoviesDataset.csv') as temp_csv:
        disney_csv_dict = csv.DictReader(temp_csv)
        for row in disney_csv_dict:
            old_release = row['Release date (datetime)']
            corrected = datetime.strptime(old_release, '%Y-%m-%d')
            if (new_year - corrected) < time_delta:
                movie_dict[row['']] = row
    random_id = random.choice(list(movie_dict))
    print("You have " + str(len(movie_dict)) + " movies to choose from")
    print(movie_dict[random_id]['title'])


def print_date():
    provided_year = input('What year?: ')
    return_date = datetime.strptime(provided_year + "/01/01", '%Y/%m/%d')
    print(return_date)


