import requests


class Dictionaries:

    domain = 'https://api.hh.ru/'

    def __init__(self):
        self.currency = dict()
        self.areas = dict()

    def init_currency(self):
        url_dict = f'{self.domain}dictionaries'
        result = requests.get(url_dict).json()
        currency = result['currency']
        for cur in currency:
            self.currency[cur['code']] = cur['rate']
        return self.currency

    def init_areas(self):
        url_dict = f'{self.domain}areas'
        result = requests.get(url_dict).json()
        self.get_areas(result)
        return self.areas

    def get_areas(self, lst):
        if len(lst) > 0:
            for el in lst:
                self.areas[el['name']] = el['id']
                self.get_areas(el['areas'])
        else:
            pass


class Vacancy:

    def __init__(self):
        self.salary_list = []
        self.skills = dict()

    def get_salary(self, vac_dict={}, cur_dict={}):
        salary = vac_dict['salary']
        try:
            low = salary['from']
            high = salary['to']
            gross = 0.87 if salary['gross'] else 1
            cur = salary['currency']
            if isinstance(low, int) and isinstance(high, int):
                low = round(low * gross / cur_dict[cur])
                high = round(high * gross / cur_dict[cur])
            elif isinstance(low, int):
                high = round(low * gross / cur_dict[cur])
                low = round(low * gross / cur_dict[cur])
            elif isinstance(high, int):
                low = round(high * gross / cur_dict[cur])
                high = round(high * gross / cur_dict[cur])
            else:
                pass
            self.salary_list.append({'low': low, 'high': high})
        except TypeError:
            pass

    def get_skills(self, skill_dict={}):
        skills_list = skill_dict['key_skills']
        for skill in skills_list:
            try:
                self.skills[skill['name']] += 1
            except:
                self.skills[skill['name']] = 1
