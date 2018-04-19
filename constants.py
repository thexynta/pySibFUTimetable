from enum import Enum
import datetime


class MyTime(datetime.time):
    def __add__(self, time):
        if isinstance(time, datetime.time):
            over = (self.minute+time.minute) // 60
            time = time.replace(minute=self.minute+time.minute - 60*over)
            if (self.hour + time.hour + over) > 23:
                time = time.replace(hour=self.hour + time.hour + over - 24)
            else:
                time = time.replace(hour=self.hour + time.hour + over)
            return time
        else:
            raise TypeError("type(group) must be %s" % type(datetime.time))

    def __sub__(self, time):
        if isinstance(time, datetime.time):
            over = 1 if self.minute < time.minute else 0

            if self.hour == 0:
                return time.replace(hour=abs(24 - over - time.hour), minute=abs(60*over - abs(self.minute - time.minute)))
            else:
                return time.replace(hour=abs(self.hour - over - time.hour), minute=abs(60*over - abs(self.minute - time.minute)))
        else:
            raise TypeError("type(group) must be %s" % type(datetime.time))


TOKEN = '517964933:AAHzA1wHMDmLLb559brQKTWsxr0lq1mJrOQ'

# htmlTimetableParser
URL_TIMETABLES = 'http://edu.sfu-kras.ru/timetable'
TIMETABLE_REQUEST = 'http://edu.sfu-kras.ru/timetable?group='
LESSON_TIME = {'1': (MyTime(8,  30), MyTime(10, 5)),
               '2': (MyTime(10, 15), MyTime(11, 50)),
               '3': (MyTime(12,  0), MyTime(13, 35)),
               '4': (MyTime(14, 10), MyTime(15, 45)),
               '5': (MyTime(15, 55), MyTime(17, 30)),
               '6': (MyTime(17, 40), MyTime(19, 15)),
               '7': (MyTime(19, 25), MyTime(21, 00))}
DAYS_WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
ODD_MESSAGE = 'Идёт нечётная неделя.'
EVEN_MESSAGE = 'Идёт чётная неделя.'
EMPTY = 'Empty'
DAYOFF = 'Выходной'
ODD = 1
EVEN = 0

# Messages from bot

START_MESSAGE = """/group, чтобы я запомнил твою группу или просто введи название группы и я напишу тебе расписание на сегодня.
                    Еще можешь посмотреть /help"""
HELP_MESSAGE = ("/start - Старт\n"
                "/stop  - Стоп\n"
                "/help  - Вывод этого сообщения\n"
                "/group - Задать группу\n"
                "/tt    - Получить расписание на сегодня\n"
                "/reset - Сброс\n"
                "\n"
                "Для ввода группы (если не знаешь, как она точно прописана в расписании), рекомендую"
                " не полностью вводить название группы (без подгруппы)."
                " Например, ввод КИ16-02 выдаст несколько групп из которых можно выбрать свою.")
ERROR_GROUP_MESSAGE = """Не удалось найти такую группу."""
CHOICE_GROUP_MESSAGE = """Выбери нужную группу:"""

# files
SQLITE_FILENAME = "users.sqlite"
GROUPS_FILENAME = 'GROUPS'
PID_FILENAME = "bot.pid"


class States(Enum):
    START = "0"
    ADD_GROUP = "1"
    CHOICE_GROUP = "2"
    ACCEPT_GROUP = "3"
    MAIN_MENU = "4"
    COMMANDS_HANDLE = "5"
    SEND_TIMETABLE = "6"
    SETTINGS = "7"