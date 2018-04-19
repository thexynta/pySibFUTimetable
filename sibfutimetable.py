import constants
import requests
import lxml.html as html
import datetime
import os
import pickle


class Groups:
    def __init__(self, *group):
        self.group, *self.subgroup = ' '.join(group).split(' (', maxsplit=1)
        self.subgroup = ''.join(self.subgroup)

        if self.group == '':
            self.group = None

        if self.subgroup == '':
            self.subgroup = None
        else:
            self.subgroup = '(' + self.subgroup

    def __str__(self):
        if self.subgroup is None:
            return self.group
        elif self.group is None:
            return None
        else:
            return self.group + ' ' + self.subgroup

    def __eq__(self, other):
        if isinstance(other, Groups):
            return self.group == other.group and self.subgroup == other.subgroup
        else:
            raise TypeError("unsupported type(s) for operator ==: %s" % type(other).__name__)

    def __contains__(self, item):
        if isinstance(item, Groups):
            return self.group == item.group and self.subgroup == item.subgroup
        else:
            raise TypeError("unsupported type(s) for operator in: %s" % type(item).__name__)

    def full(self):
        if self.subgroup is None:
            return self.group
        elif self.group is None:
            return None
        else:
            return self.group + ' ' + self.subgroup


class SibFUTimetable:
    def __init__(self, group=None, url=constants.URL_TIMETABLES, local=True):
        if isinstance(group, Groups) or group is None:
            self.url = url
            self.group = group
            self.local = local
            self._timetable = None
            if self.group is not None:
                self._get_raw_timetable()
        else:
            raise TypeError("Arg group must be %s" % type(Groups).__name__)

    def __get_request(self):
        if self.group is None:
            raise ValueError("Arg group is None")
        """
        Сайт СФУ самый лучший. Непонятно откуда у некоторых групп взялись плюсики.
        Поэтому в первом if обрабатываем исключительные группы
        """
        # ВЦ16-03РТВ (1 подгруппа)
        # ВЦ15-03РТВ (1 подгруппа)
        # +1+подгруппа

        exceptions = (Groups('ВЦ16-03РТВ (1 подгруппа)'),
                      Groups('ВЦ15-03РТВ (1 подгруппа)'))
        if self.group in exceptions:
            if self.group == exceptions[0]:  # ВЦ16-03РТВ (1 подгруппа)
                return constants.TIMETABLE_REQUEST + 'ВЦ16-03РТВ+%28+1+подгруппа%29'
            elif self.group == exceptions[1]:  # ВЦ15-03РТВ (1 подгруппа)
                return constants.TIMETABLE_REQUEST + 'ВЦ15-03РТВ+%28+1+подгруппа%29'
        if self.group.subgroup:  # Если есть подгруппа
            group = self.group.full()
        else:
            group = self.group.group

        request = constants.TIMETABLE_REQUEST + group.replace('/', '%2F')

        return constants.TIMETABLE_REQUEST + \
            group.replace('/', '%2F').replace('(', '%28').replace(' ', '+').replace(')', '%29')

    def __filename_parser(self):
        if self.group is None:
            raise ValueError("Arg group is None")
        return self.group.full().replace(' ', '').replace('/', '').replace('-', '').replace(')', '').replace('(', '').upper()

    def write(self):
        if self.group is None:
            raise ValueError("Arg group is None")
        if self._timetable is None:
            raise ValueError("Timetable is None. Nothing to write")
        try:
            os.mkdir(os.getcwd() + '/timetables')
        except FileExistsError:
            pass
        filename = os.getcwd() + '/timetables/' + self.__filename_parser()

        with open(filename, 'wb') as file:
            pickle.dump(self._timetable, file)

    def read(self):
        if self.group is None:
            raise ValueError("Arg group is None")
        filename = os.getcwd() + '/timetables/' + self.__filename_parser()

        with open(filename, 'rb') as file:
            self._timetable = pickle.load(file)

    def __get_raw_timetable(self):
        if self.group is None:
            raise ValueError("Arg group must be not None")
        """

        timetable[i][0] - День недели,'№', номер занятия
        timetable[N][2][i] - (нечетная) Название, тип, преподаватель, кабинет,
                                где N такой, что timetable[N][0] - номер занятия.
        timetable[N][3][i] - (четная) Название, тип, преподаватель, кабинет, где N такой,
                                что timetable[N][0] - номер занятия.
                                Если IndexError, то одно и тоже занятие каждую неделю.

        Возвращает список, в котором можно получить любой элемент по индексу.
        timetable[Нечетная/Четная неделя(0-1)][День недели, пн-сб(0-5)][лента(0-6)]

        """
        page = requests.get(self.__get_request())
        tree = html.fromstring(page.content)
        raw_timetable = tree.xpath("//table[@class=\"table timetable\"]/*")

        raw_timetable.append('Воскресенье')  # Для правильной работы алгоритма

        timetable_final = [[], []]
        tmp_tt_odd = []
        tmp_tt_even = []
        tmp = [[], []]
        for i in raw_timetable:
            try:
                current = i[0].text_content()
            except AttributeError:
                current = i
            if current in constants.DAYS_WEEK and current != 'Понедельник':

                # Нечетная неделя
                if not tmp[0]:
                    timetable_final[0].append(constants.DAYOFF)
                else:
                    timetable_final[0].append(tmp[0][:])
                # Четная неделя
                if not tmp[1]:
                    timetable_final[1].append(constants.DAYOFF)
                else:
                    timetable_final[1].append(tmp[1][:])

                tmp = [[], []]
                continue

            if current in constants.LESSON_TIME:
                tmp_tt_odd = []
                tmp_tt_even = []
                tmp_tt_odd.append(current)  # добавляем номер занятия в начало
                tmp_tt_even.append(current)  #

                if i[2].text_content() != '':  # занятие на нечетной неделе
                    for j in i[2]:
                        if j.text_content() != '':
                            tmp_tt_odd.append(j.text_content())
                        if j.tail is not None:  # в tail хранится тип занятия или None
                            tmp_tt_odd.append(j.tail[1:])  # первый символ пробел
                else:
                    tmp_tt_odd.pop()

                try:
                    if i[3].text_content() != '':  # занятие на четной неделе
                        for j in i[3]:
                            if j.text_content() != '':
                                tmp_tt_even.append(j.text_content())
                            if j.tail is not None:  # в tail хранится тип занятия или None
                                tmp_tt_even.append(j.tail[1:])  # первый символ пробел
                    else:
                        tmp_tt_even.pop()
                except IndexError:  # если i[3] не существует, значит занятие на четной такое же, как и на нечетной
                    for j in i[2]:
                        if j.text_content() != '':
                            tmp_tt_even.append(j.text_content())
                        if j.tail is not None:  # в tail хранится тип занятия или None
                            tmp_tt_even.append(j.tail[1:])  # первый символ пробел
                if tmp_tt_odd:
                    tmp[0].append(tmp_tt_odd[:])
                if tmp_tt_even:
                    tmp[1].append(tmp_tt_even[:])
        if timetable_final:
            self._timetable = timetable_final
        else:
            self._timetable = None

    def _get_raw_timetable(self):
        if self.local:
            self.read()
        elif self.local is False:
            self.__get_raw_timetable()
        else:
            return False

    def get_groups(self):
        if self.local:
            filename = os.getcwd() + '/timetables/GROUPS'
            with open(filename, 'r') as file:
                return [Groups(i.rstrip()) for i in file.readlines()]
        if self.local is False:
            page = requests.get(self.url)

            tree = html.fromstring(page.content)
            raw_groups = tree.xpath(".//div[@class=\"collapsed-content\"]/ul/li/a[@href]/text()")

            return [Groups(i.replace('\xa0', ' ')) for i in raw_groups]

    def get_day(self,
                week_number=datetime.datetime.today().isocalendar()[1],
                week_day=datetime.datetime.today().weekday()):
        if 0 <= week_day <= 5 and week_number >= 0:
            week_number = constants.ODD if week_number % 2 == 0 else constants.EVEN  # 0 - нечетная, 1 четная недели
            try:
                return self._timetable[week_number][week_day]
            except IndexError:
                return None
        elif week_day == 6:
            return None
        else:
            raise ValueError('week_day must be in [0, 5] and week_number [0, ...) not %d, %d' % (week_day, week_number))

    def get_week(self, week_number=datetime.datetime.today().isocalendar()[1]):
        if week_number >= 0:
            week_number = constants.EVEN if week_number % 2 == 0 else constants.ODD
            try:
                return self._timetable[week_number]
            except IndexError:
                return None
        else:
            raise ValueError('week_number must be in [0, ...) not %d' % (week_number))

    def set_group(self, group):
        self.group = Groups(group)

    def save_groups(self, *groups):
        try:
            os.mkdir(os.getcwd() + '/timetables')
        except FileExistsError:
            pass
        filename = os.getcwd() + '/timetables/GROUPS'
        with open(filename, 'w') as file:
            for i in groups:
                if not isinstance(i, Groups):
                    raise TypeError("%s is not Groups type" % i)
                file.write(i.full() + '\n')


def save_timetables_local():
    """

    Моя функция личная. Что хочу, то и делаю

    """
    groups = SibFUTimetable(local=False).get_groups()
    SibFUTimetable().save_groups(*groups)
    count = 0
    progress_cur = 0
    progress_to = len(groups) / 100

    for i in groups:
        SibFUTimetable(group=i, local=False).write()
        count += 1
        if count > (progress_to*progress_cur + 1):
            progress_cur += 1
        print(str(progress_cur) + '%       (' + str(count) + '/' + str(len(groups)) + ')')

# save_timetables_local()
