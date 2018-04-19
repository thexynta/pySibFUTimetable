#!/usr/bin/python3

import sys
import constants
import sibfutimetable as tt
import sqlite3
from telebot import TeleBot
import os
from datetime import datetime

try:
    with open(constants.PID_FILENAME, 'r') as pid:
        os.kill(int(pid.readline()), 19)
except Exception as e:
    pass

time = sys.argv[1] + ':' + sys.argv[2]
bot = TeleBot(constants.TOKEN)

conn = sqlite3.connect(constants.SQLITE_FILENAME)
cursor = conn.cursor()
cursor.execute("SELECT `user_id`, `group` FROM users WHERE `alarm` = :alarm", {"alarm": time})
job = cursor.fetchall()

for i in job:
    user_id = i[0]
    group = tt.Groups(i[1])
    raw_timetable = tt.SibFUTimetable(group=group).get_day()
    if raw_timetable is None:
        msg_to_user = '<i>' + constants.DAYS_WEEK[datetime.today().weekday()] + ' ' + str(datetime.today().date()) + '</i>\n'
        msg_to_user += 'Выходной\n\n'
        break
    msg_to_user = '<i>' + constants.DAYS_WEEK[datetime.today().weekday()] + ' ' + str(datetime.today().date()) + '</i>\n'
    for lesson in raw_timetable:
        for j, val in enumerate(lesson):
            if j == 0:
                msg_to_user += '<b>' + val + '</b> '
            else:
                msg_to_user += val + '\n'
        msg_to_user += '\n'

    bot.send_message(user_id, msg_to_user, parse_mode='HTML')
conn.close()

try:
    with open(constants.PID_FILENAME, 'r') as pid:
        os.kill(int(pid.readline()), 18)
except Exception as e:
    pass
