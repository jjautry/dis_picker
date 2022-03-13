import random
from datetime import datetime


def dis_countdown():
   today = datetime.today().date()
   disney_date = datetime(2022, 10, 9).date()
   delta = disney_date - today
   return delta.days

