import requests
import vacancy_func as vac

class Search:

    DOMAIN = 'https://api.hh.ru/'
    url_vacancies = f'{DOMAIN}vacancies'

    def __init__(self):
        hh_dict = vac.Dictionaries()
        self.areas_dict = hh_dict.init_areas()
        self.cur_dict = hh_dict.init_currency()
        self.search_strict = False
        self.vacancies_data = vac.Vacancy()
        self.search_area = 'None'
        self.search_vacancy = ''
        self.params = dict()
        self.search_count = 0
        self.pages = 0
        self.requirement_count = 0
        self.result = dict()
        self.params['period'] = 3
        self.params['per_page'] = 100

    def set_search_text(self, strict):
        self.search_strict = True if strict == 'y' else False
        self.params['text'] = f'\"{self.search_vacancy}\"' if self.search_strict else self.search_vacancy

    def set_area(self, area):
        self.search_area = area
        self.params['area'] = self.areas_dict[area]

    def get_search_data(self):
        self.search_result = requests.get(self.url_vacancies, params=self.params).json()

    def get_vacancies_data(self):
        items = self.search_result['items']
        for i in range(len(items)):
            url_vacancy = items[i]['url']
            result_vacancy = requests.get(url_vacancy).json()
            self.vacancies_data.get_skills(result_vacancy)
            self.vacancies_data.get_salary(result_vacancy, self.cur_dict)

    def get_result(self):
        cnt = 0
        for skill in self.vacancies_data.skills:
            cnt += self.vacancies_data.skills[skill]
        # заглушка на деление на 0
        if cnt == 0:
            cnt = 1
        list_skill = [{'name': skill, 'count': self.vacancies_data.skills[skill],
                       'percent': round(self.vacancies_data.skills[skill] * 100 / cnt, 1)} for skill in
                      self.vacancies_data.skills]
        list_skill = sorted(list_skill, key=lambda x: x['count'], reverse=True)
        # выбираем топ 5
        res_list = []
        res_cnt = 0
        if len(list_skill) > 1:
            for i in range(len(list_skill)-1):
                res_list.append(list_skill[i])
                res_cnt += list_skill[i]['count']
                if list_skill[i]['count'] == list_skill[i + 1]['count']:
                    continue
                else:
                    if len(res_list) >= 5:
                        break
                    else:
                        continue
        list_skill = res_list
        list_skill.append({'name':'other', 'count':cnt - res_cnt, 'percent': round((1-res_cnt/cnt)*100, 1)})


        cnt_salary = len(self.vacancies_data.salary_list)
        low = 0
        high = 0
        if cnt_salary > 0:
            for salary in self.vacancies_data.salary_list:
                low += salary['low']
                high += salary['high']
        else:
            cnt_salary = 1 #чтобы уйти от деления на 0
        self.result['keywords'] = self.search_vacancy
        self.result['search_strict'] = self.search_strict
        self.result['area'] = self.search_area
        self.result['count'] = self.search_count
        self.result['salary'] = {'from': round(low / cnt_salary), 'to': round(high / cnt_salary), 'vacancy_with_salary': cnt_salary}
        self.result['vacancy_for_requirements'] = self.requirement_count
        self.result['requirements'] = list_skill

    def search_first(self):
        self.params['page'] = 0
        self.get_search_data()
        self.search_count = self.search_result['found']
        self.requirement_count = 2000 if self.search_count > 2000 else self.search_count
        self.pages = self.search_result['pages']
        if self.search_count > 0:
            self.get_vacancies_data()

    def search_last(self):
        if self.pages > 1:
            for page in range(1, self.pages):
                self.params['page'] = page
                self.get_search_data()
                self.get_vacancies_data()
        else:
            pass