import search_func as search
import json

search_req = search.Search()

if __name__ == '__main__':


    search_req.search_vacancy = input('Введите вакансию для поиска: ')

    # строгий поиск
    strict_search = ''
    while strict_search not in ['y', 'n']:
        strict_search = input('Строгий поиск: y/n ').lower()
    search_req.set_search_text(strict_search)

    # поиск по региону
    search_by_area = ''
    while search_by_area not in ['y','n']:
        search_by_area = input('Нужен поиск по региону? y/n ').lower()
        if search_by_area == 'y':
            area_str='_'
            while area_str not in search_req.areas_dict:
                area_str = input('Введите регион поиска: ')
            search_req.set_area(area_str)

    # поиск
    search_req.params['page'] = 0
    search_req.get_search_data()
    search_req.search_count = search_req.search_result['found']
    search_req.requirement_count = 2000 if search_req.search_count > 2000 else search_req.search_count
    pages = search_req.search_result['pages']

    if search_req.search_count == 0:
        print('Вакансии не найдены, измените критерии')
    else:
        print('Всего найдено вакансий', search_req.search_count)
        search_req.get_vacancies_data()
        print(f'обработано {min(search_req.search_count, search_req.per_page)}')
        if pages > 1:
            for page in range(1, pages):
                search_req.params['page'] = page
                search_req.get_search_data()
                search_req.get_vacancies_data()
                print(f'обработано {min(search_req.search_count, search_req.per_page * (page + 1))}')

    # запись в файл
    search_req.get_result()
    res = json.dumps(search_res.result)
    with open('search_result.json', 'w') as f:
        f.write(f'{res}\n')


