import vacancy_func as vac
import search_func as search

vacancy_str = input('Введите вакансию для поиска: ')
vacancy_list = vacancy_str.split()
params = dict()
search_res = search.Search()

# точный поиск
if len(vacancy_list) > 1:
    strict_search = ''
    while strict_search not in ['y', 'n']:
        strict_search = input('Строгий поиск: y/n ').lower()
    if strict_search == 'y':
        params['text'] = f'\"{vacancy_str}\"'
    else:
        params['text'] = vacancy_str
else:
    params['text'] = vacancy_str

hh_dict = vac.Dictionaries()

# поиск по региону
search_by_area = ''
while search_by_area not in ['y','n']:
    search_by_area = input('Нужен поиск по региону? y/n ').lower()
search_by_area_res = True if search_by_area == 'y' else False
if search_by_area_res:
    area_str = ''
    hh_dict.init_areas()
    search_res.areas_dict = hh_dict.areas
    while area_str not in search_res.areas_dict:
        area_str = input('Введите регион поиска: ')
    params['area'] = search_res.areas_dict[area_str]
params['page'] = 0

search_res.get_search_data(params)
search_count = search_res.result['found']
pages = search_res.result['pages']

print('Всего найдено вакансий', search_count)

if search_count == 0:
    print('Вакансии не найдены, измените критерии')
else:
    hh_dict.init_currency()
    search_res.vacancies_data.currency = hh_dict.currency
    search_res.get_vacancies_data()
    print(f'обработано {min(search_count, search_res.per_page)}')
    if pages > 1:
        for page in range(1, pages):
            params['page'] = page
            search_res.get_search_data(params)
            search_res.get_vacancies_data()
            print(f'обработано {min(search_count, search_res.per_page * (page + 1))}')

cnt = 0
for skill in search_res.vacancies_data.skills:
    cnt += search_res.vacancies_data.skills[skill]
list_skill = [{'name': skill, 'count': search_res.vacancies_data.skills[skill],
               'percent':round(search_res.vacancies_data.skills[skill] * 100 / cnt, 1) } for skill in search_res.vacancies_data.skills]
list_skill = sorted(list_skill, key = lambda x: x['count'], reverse = True)
print(list_skill)

cnt = len(search_res.vacancies_data.salary_list)
low = 0
high = 0
for salary in search_res.vacancies_data.salary_list:
    low += salary['low']
    high += salary['high']
print(f' average salary: from {round(low / cnt)} to {round(high / cnt)} by {cnt} vacancies with salary')