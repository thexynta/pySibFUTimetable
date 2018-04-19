#!/usr/bin/python3

import sqlite3
import constants


# получаем поле из бд по user_id
def get_element(element, user_id):
    conn = sqlite3.connect(constants.SQLITE_FILENAME)
    cursor = conn.cursor()
    cursor.execute('SELECT {0} FROM users WHERE `user_id` = {1}'.format(element, user_id))
    value = cursor.fetchall()[0][0]
    conn.close()
    return value


def set_time(user_id, time):
    if time < -1:
        return False
    conn = sqlite3.connect(constants.SQLITE_FILENAME)
    cursor = conn.cursor()

    cursor.execute("SELECT `user_id`, `group` FROM users WHERE `user_id` = {0} AND `group` != ''".format(user_id))
    i = cursor.fetchall()[0]  # job[][0] - user_id, job[][1] - group

    try:
        cursor.execute("UPDATE users SET `time` = :time WHERE `user_id` = :user_id",
                       {"user_id": user_id,
                        "time": time})
    except Exception as e:
        pass
    conn.commit()
    conn.close()


def create_db():
    conn = sqlite3.connect(constants.SQLITE_FILENAME)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE users (
                                          `user_id` TEXT,
                                          `name` TEXT,
                                          `group` TEXT,
                                          `time` TEXT DEFAULT "-1",
                                          `alarm` TEXT,
                                          `current_state` TEXT DEFAULT "0",
                                          PRIMARY KEY(`user_id` ASC))""")
    conn.close()


def insert_or_update(user_id, first_name, group):
    conn = sqlite3.connect(constants.SQLITE_FILENAME)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (`user_id`, `name`, `group`) VALUES (:user_id, :name, :group)',
                       {'user_id': user_id,
                        'name':  first_name,
                        'group': group})
    except sqlite3.IntegrityError:
        cursor.execute('UPDATE users SET `group` = :group, `name` = :name WHERE `user_id` = :user_id',
                       {'user_id': user_id,
                        'group': group,
                        'name': first_name})
    conn.commit()
    conn.close()


# Пытаемся узнать из базы «состояние» пользователя
def get_current_state(user_id):
    conn = sqlite3.connect(constants.SQLITE_FILENAME)
    cursor = conn.cursor()
    cursor.execute("SELECT `current_state` FROM users WHERE `user_id` = :user_id",
                           {'user_id': user_id})
    try:
        state = cursor.fetchall()[0][0]  # получаем первый элемент первого кортежа списка [(_value_, ...), ...]
    except IndexError:
        return constants.States.START.value
    conn.close()
    return state


# Сохраняем текущее «состояние» пользователя в нашу базу
def set_state(user_id, value):
    conn = sqlite3.connect(constants.SQLITE_FILENAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET `current_state` = :value WHERE `user_id` = :user_id",
                   {'user_id': user_id,
                    'value': value})
    conn.commit()
    conn.close()

#create_db()
