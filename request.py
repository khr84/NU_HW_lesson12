import search_func as search
import json
import db_func as dbf
import db_func_orm as dbfo

if __name__ == '__main__':
    search_req = search.Search()
    search_req.search_vacancy = input('Введите вакансию для поиска: ')

    # строгий поиск
    strict_search = ''
    while strict_search not in ['y', 'n']:
        strict_search = input('Строгий поиск: y/n ').lower()
    search_req.set_search_text(strict_search)

    # поиск по региону
    search_by_area = ''
    while search_by_area not in ['y', 'n']:
        search_by_area = input('Нужен поиск по региону? y/n ').lower()
        if search_by_area == 'y':
            area_str = '_'
            while area_str not in search_req.areas_dict:
                area_str = input('Введите регион поиска: ')
            search_req.set_area(area_str)

    # поиск
    search_req.search_first()
    if search_req.search_count == 0:
        print('Вакансии не найдены, измените критерии')
    else:
        print('Всего найдено вакансий', search_req.search_count)
        search_req.search_last()
        print('Обрабатаны все вакансии')

        # запись в файл
        search_req.get_result()
        res = json.dumps(search_req.result)
        with open('search_result.json', 'w') as f:
            f.write(f'{res}\n')
        dbf.write_db(search_req.result)
        # dbfo.db_orm_check_vac(search_req.result)
        # dbfo.db_orm_import_vacancy(search_req.result)
        # dbfo.db_orm_import_salary(search_req.result)
        # dbfo.db_orm_import_skill(search_req.result)
        # dbfo.db_orm_import_vac_to_skill(search_req.result)
