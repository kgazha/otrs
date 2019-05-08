# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 12:56:07 2018
@author: gazhakv
"""
from dateutil import parser
import calendar
import configparser


config = configparser.ConfigParser()
config.read('settings.ini')

YEAR = int(config['DATES']['YEAR'])
LUNCH = range(43200, 45900)
HOLIDAYS = config['DATES']['HOLIDAYS']
HOLIDAYS = [i.strip(',') for i in HOLIDAYS.split()]
WORKING_DATES = config['DATES']['WORKING_DATES']
WORKING_DATES = [i.strip(',') for i in WORKING_DATES.split()]


def convert_to_seconds(hours, minutes):
    return hours * 3600 + minutes * 60


class EmployeeWorkingTime:
    def __init__(self, start_hour, end_hour, start_minute, end_minute, friday_end_hour=None, friday_end_minute=None):
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.start_minute = start_minute
        self.end_minute = end_minute
        if friday_end_hour:
            self.friday_end_hour = friday_end_hour
        else:
            self.friday_end_hour = end_hour
        if friday_end_minute:
            self.friday_end_minute = friday_end_minute
        else:
            self.friday_end_minute = end_minute

    def compute_working_time(self, start_date, end_date, dayfirst=False, result_in_hours=True):
        start = parser.parse(start_date, dayfirst=dayfirst)
        end = parser.parse(end_date, dayfirst=dayfirst)
        result = 0
        for month in range(start.month, end.month + 1):
            days = end.day + 1
            first_day = start.day
            if month != end.month:
                days = calendar.monthrange(start.year, month)[1] + 1
            if month != start.month:
                first_day = 1
            for day in range(first_day, days):
                next_date = str(day) + '.' + str(month) + '.' + str(start.year)
                next_date = parser.parse(next_date, dayfirst=True).date()
                if ((next_date.weekday() < 5) or
                   (next_date in [parser.parse(i, dayfirst=True).date() for i in WORKING_DATES])) and \
                   (next_date not in [parser.parse(i, dayfirst=True).date() for i in HOLIDAYS]):
                    start_hour = self.start_hour
                    start_minute = self.start_minute
                    end_hour = self.end_hour
                    end_minute = self.end_minute
                    if next_date.weekday() == 4:
                        end_hour = self.friday_end_hour
                        end_minute = self.friday_end_minute
                    if next_date == start.date():
                        if convert_to_seconds(start.hour, start.minute) >= convert_to_seconds(start_hour, start_minute):
                            start_hour = start.hour
                            start_minute = start.minute
                        if convert_to_seconds(start.hour, start.minute) >= convert_to_seconds(end_hour, end_minute):
                            start_hour = end_hour
                            start_minute = end_minute
                    if next_date == end.date():
                        if convert_to_seconds(end.hour, end.minute) <= convert_to_seconds(end_hour, end_minute):
                            end_hour = end.hour
                            end_minute = end.minute
                        if convert_to_seconds(end_hour, end_minute) <= convert_to_seconds(start_hour, start_minute):
                            start_hour = end_hour
                            start_minute = end_minute
                    converted_start = convert_to_seconds(start_hour, start_minute)
                    converted_end = convert_to_seconds(end_hour, end_minute)
                    lunch_difference = set(range(converted_start, converted_end)).difference(set(LUNCH))
                    lunch_difference = list(lunch_difference)
                    if lunch_difference:
                        converted_start = lunch_difference[0]
                        converted_end = converted_start + len(lunch_difference)
                        result += converted_end - converted_start
                    else:
                        result += 0
        if result_in_hours:
            result /= 3600
        return result


class RegularWorkingTime(EmployeeWorkingTime):
    def __init__(self):
        super().__init__(start_hour=8, end_hour=17, start_minute=30, end_minute=30,
                         friday_end_hour=16, friday_end_minute=15)


class FirstLineWorkingTime(EmployeeWorkingTime):
    def __init__(self):
        super().__init__(start_hour=0, end_hour=24, start_minute=0, end_minute=0)
