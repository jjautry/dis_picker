from datetime import datetime


def dis_countdown():
   """Takes current date and returns days left until Disney trip"""
   today = datetime.today().date()
   disney_date = datetime(2022, 10, 9).date()
   delta = disney_date - today
   return delta.days
