#!/usr/bin/python3

import constants
import sibfutimetable as tt
from sibfutimetable import Groups
import sqlite3
import os
from crontab import CronTab

groups = tt.SibFUTimetable().get_groups()

conn = sqlite3.connect(constants.SQLITE_FILENAME)
cursor = conn.cursor()

cursor.execute("SELECT `user_id`, `group`, `time` FROM users WHERE `user_id` != '' AND `group` != ''")
jobs = cursor.fetchall()  # job[][0] - user_id, job[][1] - group, job[][2] - time
for i in jobs:
    try:
		time = constants.MyTime(int(i[2]) // 60, (int(i[2]) - (int(i[2]) // 60) * 60)) # преобразование минут в (часы, минуты)
    except ValueError:
        try:
            cursor.execute("UPDATE users SET `alarm` = :time WHERE `user_id` = :user_id",
                           {"user_id": i[0],
                            "time": -1})
        except Exception as e:
            print(e)
            pass
    else:
        first_lesson = tt.SibFUTimetable(Groups(i[1])).get_day()[0][0]
        first_lesson_time = constants.LESSON_TIME.get(first_lesson)[0]
        first_lesson_time = first_lesson_time - time
        try:
            cursor.execute("UPDATE users SET `alarm` = :time WHERE `user_id` = :user_id",
                           {"user_id": i[0],
                            "time": str(first_lesson_time.hour) + ':' + str(first_lesson_time.minute)})
        except Exception as e:
            print(e)
            pass
    conn.commit()

cursor.execute("SELECT `alarm` FROM users GROUP BY (`alarm`)")
jobs = cursor.fetchall()
cron = CronTab(user=True)
# удаляем старые задачи
old_jobs = cron.find_command('cron_exec.sh')
for i in old_jobs:
    cron.remove(i)
# добавляем новые
for i in jobs:
    i = i[0]
    if i != '-1' and i is not None:
        job = cron.new(command=os.getcwd() + '/cron_exec.sh ' + i.split(':')[0] + ' ' + i.split(':')[1])
        job.hours.on(i.split(':')[0])
        job.minutes.on(i.split(':')[1])
cron.write()
