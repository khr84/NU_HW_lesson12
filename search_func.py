import requests
import vacancy_func as vac

class Search:

    DOMAIN = 'https://api.hh.ru/'
    url_vacancies = f'{DOMAIN}vacancies'

    def __init__(self):
        self.per_page = 100
        self.areas_dict = dict()
        self.vacancies_data = vac.Vacancy()

    def get_search_data(self, params):
        params['per_page'] = self.per_page
        self.result = requests.get(self.url_vacancies, params=params).json()

    def get_vacancies_data(self):
        items = self.result['items']
        for i in range(len(items)):
            url_vacancy = items[i]['url']
            result_vacancy = requests.get(url_vacancy).json()
            self.vacancies_data.get_skills(result_vacancy)
            self.vacancies_data.get_salary(result_vacancy)