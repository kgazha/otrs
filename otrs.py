# -*- coding: utf-8 -*-
import MySQLdb
import pandas as pd
import numpy as np
from working_time import RegularWorkingTime, FirstLineWorkingTime
import configparser


config = configparser.ConfigParser()
config.read('settings.ini')

db = MySQLdb.connect(config['CONNECTION']['HOST'],
                     config['CONNECTION']['USER'],
                     config['CONNECTION']['PASSWORD'],
                     config['CONNECTION']['DATABASE'],
                     charset='utf8',
                     init_command='SET NAMES UTF8')

HOLIDAYS = config['DATES']['HOLIDAYS']
HOLIDAYS = [i.strip(',') for i in HOLIDAYS.split()]
WORKING_DATES = config['DATES']['WORKING_DATES']
WORKING_DATES = [i.strip(',') for i in WORKING_DATES.split()]
WAITING_STATES = config['DATES']['WAITING_STATES']
WAITING_STATES = tuple([int(i.strip(',')) for i in WAITING_STATES.split()])
START_DATE = config['DATES']['START_DATE']

cursor = db.cursor(MySQLdb.cursors.DictCursor)


def lines_working_time(df, name_emergence_time, name_lock_time, full_time=False):
    emergence_time = df[name_emergence_time]
    lock_time = df[name_lock_time]
    in_working = []
    for i in range(len(df)):
        if lock_time[i] != '\\N':
            if full_time:
                result = FirstLineWorkingTime().compute_working_time(emergence_time[i], lock_time[i], False)
            else:
                result = RegularWorkingTime().compute_working_time(emergence_time[i], lock_time[i], False)
        else:
            result = ''
        in_working.append(result)
    return in_working


def close_time_calculation(df):
    auto_close = []
    forced_close = []
    for i in range(len(df)):
        if df['auto_close'][i] != '\\N':
            result = RegularWorkingTime().compute_working_time(df['tcreatetime'][i], df['auto_close'][i], False)
        else:
            result = ''
        auto_close.append(result)
        if df['closed'][i] != '\\N':
            result = RegularWorkingTime().compute_working_time(df['tcreatetime'][i], df['closed'][i], False)
        else:
            result = ''
        forced_close.append(result)
    df['auto_closed'] = auto_close
    df['forced_close'] = forced_close


def get_waiting_ticket_ids():
    sql_waiting_states = open('waiting_states.sql').read().splitlines()
    sql_waiting_states = ' '.join(sql_waiting_states).format(START_DATE, WAITING_STATES)
    [cursor.execute(sql) for sql in sql_waiting_states.format(START_DATE).split(';')]
    data = cursor.fetchall()
    waiting_ticket_ids = list(map(lambda x: list(x.values())[0], data))
    return waiting_ticket_ids


def get_ticket_history(ticket_ids):
    sql_ticket_info = open('ticket_info.sql').read().splitlines()
    sql_ticket_info = ' '.join(sql_ticket_info)
    cursor.execute(sql_ticket_info.format(str(tuple(ticket_ids))))
    data = cursor.fetchall()
    ticket_history = list(map(lambda x: list(x.values()), data))
    return ticket_history


def compute_contractor_time(ticket_history_df):
    time = 0
    _start = None
    _end = None
    for idx, row in ticket_history_df.iterrows():
        if row[1] in WAITING_STATES:
            _start = row[3]
        elif _start:
            _end = row[3]
            diff = RegularWorkingTime().compute_working_time(_start.strftime("%Y-%m-%d %H:%M"),
                                                             _end.strftime("%Y-%m-%d %H:%M"))
            time += diff
            _start, _end = None, None
    return time


def stuff(result):
    sql_waiting_states = open('waiting_states.sql').read().splitlines()
    sql_waiting_states = ' '.join(sql_waiting_states).format(START_DATE, WAITING_STATES)

    c = db.cursor(MySQLdb.cursors.DictCursor)
    [c.execute(sql) for sql in sql_waiting_states.format(START_DATE).split(';')]
    data = c.fetchall()
    waiting_ticket_ids = list(map(lambda x: list(x.values())[0], data))

    sql_ticket_info = open('ticket_info.sql').read().splitlines()
    sql_ticket_info = ' '.join(sql_ticket_info)

    c.execute(sql_ticket_info.format(str(tuple(waiting_ticket_ids))))
    data = c.fetchall()
    ticket_history = list(map(lambda x: list(x.values()), data))

    sql_ticket_info = {x: [] for x in waiting_ticket_ids}
    df = pd.DataFrame(ticket_history)

    def compute_contractor_time(task):
        time = 0
        _start = None
        _end = None
        for idx, row in task.iterrows():
            if row[1] in WAITING_STATES:
                _start = row[3]
            elif _start:
                _end = row[3]
                diff = RegularWorkingTime().compute_working_time(_start.strftime("%Y-%m-%d %H:%M"),
                                                                 _end.strftime("%Y-%m-%d %H:%M"))
                time += diff
                _start, _end = None, None
        return time

    for k in sql_ticket_info.keys():
        sql_ticket_info[k] = compute_contractor_time(df[df[2] == k])

    for idx, val in result.iterrows():
        if val.tid in sql_ticket_info.keys():
            if val['forced_close']:
                if val['forced_close'] > sql_ticket_info[val.tid]:
                    result.at[idx, 'forced_close'] = val['forced_close'] - sql_ticket_info[val.tid]
            if val['auto_closed']:
                if val['auto_closed'] > val['forced_close']:
                    result.at[idx, 'auto_closed'] = val['auto_closed'] - sql_ticket_info[val.tid]
        try:
            if result.at[idx, 'artbody'] is not np.nan:
                result.at[idx, 'artbody'] = result.at[idx, 'artbody'][:1000]
        except:
            print(idx, result.at[idx, 'artbody'])
            raise 123
    result.to_csv('report_final_result2.csv', sep=';', encoding='ansi', decimal=',')


def subtract_waiting_time(df):
    waiting_ticket_ids = get_waiting_ticket_ids()
    ticket_history = get_ticket_history(waiting_ticket_ids)
    waiting_ticket_dict = {x: [] for x in waiting_ticket_ids}
    ticket_history_df = pd.DataFrame(ticket_history)
    for k in waiting_ticket_dict.keys():
        waiting_ticket_dict[k] = compute_contractor_time(ticket_history_df[ticket_history_df[2] == k])
    for idx, val in df.iterrows():
        if val.tid in waiting_ticket_dict.keys():
            if val['forced_close']:
                if val['forced_close'] > waiting_ticket_dict[val.tid]:
                    df.at[idx, 'forced_close'] = val['forced_close'] - waiting_ticket_dict[val.tid]
            if val['auto_closed']:
                if val['auto_closed'] > val['forced_close']:
                    df.at[idx, 'auto_closed'] = val['auto_closed'] - waiting_ticket_dict[val.tid]
            # if df.at[idx, 'artbody'] is not np.nan:
        if df.at[idx, 'artbody']:
            df.at[idx, 'artbody'] = df.at[idx, 'artbody'][:1000]


def compute():
    df = pd.read_csv('report2.csv', sep=';', encoding='ansi')
    close_time_calculation(df)
    df['in_working_first'] = lines_working_time(df, 'first_line_emergence_time', 'first_move_or_lock_time', True)
    df['in_working_others'] = lines_working_time(df, 'others_line_emergence_time', 'others_line_lock_time')
    df['others_line_message_time'] = lines_working_time(df, 'others_line_emergence_time', 'others_line_message_time')
    # stuff(df)
    subtract_waiting_time(df)
    df.to_csv('report_computed.csv', sep=';', encoding='ansi', decimal=',')


if __name__ == '__main__':
    compute()
