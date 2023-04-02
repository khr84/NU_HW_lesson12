from datetime import datetime
import requests
import vacancy_func as vac
import sqlite3
conn = sqlite3.connect('sqlite.db', check_same_thread=False)


def read_db(date_beg, date_end):
    vac_list = []
    cursor = conn.cursor()
    sql = f'select v.id, v.name, v.strict_search, v.count_vac, r.reg_name, s.low, s.high, s.count, v.search_date \
          from search_vac v join region r on r.reg_id = v.region_id \
            join salary s on s.id = v.id where v.search_date >= \"{date_beg}\" and v.search_date < \"{date_end}\"'
    cursor.execute(sql)
    result_list = cursor.fetchall()
    result_list.sort(key=lambda x: x[-1], reverse=True)
    for res in result_list:
        sql = f'select s.skill_name, vs.percent from vac_to_skill vs join skill s on vs.skill_id = s.skill_id where vs.vac_id = {res[0]}'
        cursor.execute(sql)
        skill_list = cursor.fetchall()
        skill_list.sort(key=lambda x: x[-1], reverse=True)
        vac_dict = {}
        vac_dict['vacancy'] = res[1]
        vac_dict['strict'] = 'Да' if res[2] == 1 else 'Нет'
        vac_dict['count'] = res[3]
        vac_dict['area'] = res[4]
        vac_dict['salary'] = f'Средняя ЗП от {res[5]} до {res[6]}, определено по {res[7]} вакансиям с ЗП'
        vac_dict['date'] = res[8]
        skill_vac = []
        for skill in skill_list:
            skill_vac.append((skill[0], skill[1]))
        vac_dict['skill'] = skill_vac
        vac_list.append(vac_dict)
    cursor.close
    return vac_list

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

    def write_db(self):
        if self.search_count == 0:
            pass
        else:
            # ==================insert regions
            cursor = conn.cursor()
            region_list = list(self.areas_dict.items())
            # добавим дефолтное значение если регион не указан
            region_list.append(('None', -1000))
            for i in range(len(region_list)):
                sql_reg = f'select {region_list[i][1]} as id,\"{region_list[i][0]}\" as name'
                sql_reg = f'insert into region(reg_id, reg_name) select id, name from ({sql_reg}) t \
                            left join region r on r.reg_name = t.name where r.reg_name is null'
                cursor.execute(sql_reg)
                conn.commit()
            # ==================insert vacancy
            vacancy = f'\'\"{self.search_vacancy}\"\''
            region = self.params.get("area", -1000)
            strict = 1 if self.search_strict else 0
            sql_vac = f'select id from search_vac where name = {vacancy} and region_id = {region} and strict_search = {strict}'
            cursor.execute(sql_vac)
            res = cursor.fetchall()
            # удаление текущих значений если такая вакансия уже есть
            if res:
                sql_vac = f'delete from vac_to_skill where vac_id = {res[0][0]}'
                cursor.execute(sql_vac)
                conn.commit()
                sql_vac = f'delete from salary where id = {res[0][0]}'
                cursor.execute(sql_vac)
                conn.commit()
                sql_vac = f'delete from search_vac where id = {res[0][0]}'
                cursor.execute(sql_vac)
                conn.commit()
            # вставка новых значений
            now = datetime.now()
            current_time = now.strftime("%Y.%m.%d %H:%M:%S")
            sql_vac = f'select {vacancy} as name, {self.search_count} as count, \"{current_time}\" as search_date, {region} as reg_id, {strict} as strict'
            sql_vac = f'insert into search_vac(name, count_vac, search_date, region_id, strict_search) select * from ({sql_vac})'
            cursor.execute(sql_vac)
            conn.commit()
            # ====================insert salary
            sql_vac = f'select id from search_vac where name = {vacancy} and region_id = {region} and strict_search = {strict}'
            cursor.execute(sql_vac)
            res = cursor.fetchall()
            sql_vac = f'select {res[0][0]} as id, {self.result["salary"]["from"]} as low, {self.result["salary"]["to"]} as high, \
                        {self.result["salary"]["vacancy_with_salary"]} as count'
            sql_vac = f'insert into salary select id, low, high, count from ({sql_vac})'
            cursor.execute(sql_vac)
            conn.commit()
            # ==================insert skills
            sql_skill = ''
            for i in range(len(self.result['requirements'])-1): # (-1): убираем other
                skill = self.result["requirements"][i]["name"]
                percent = self.result["requirements"][i]["percent"]
                if i ==0:
                    sql_skill = f'select \"{skill.lower()}\" as name, {percent} as percent'
                else:
                    sql_skill = f'{sql_skill} union select \"{skill.lower()}\" as name, {percent} as percent'
            sql_skill_ins = f'insert into skill(skill_name) select name from ({sql_skill}) t \
                            left join skill s on s.skill_name = t.name where s.skill_name is null'
            cursor.execute(sql_skill_ins)
            conn.commit()
            # ====================insert vac_to_skill
            sql_vac_skill = f'select skill_id, t.percent  from skill s join ({sql_skill}) t on t.name = s.skill_name'
            cursor.execute(sql_vac_skill)
            res_list = cursor.fetchall()
            for i in range(len(res_list)):
                if i == 0:
                    sql_vac_skill = f'select {res[0][0]} as vac_id, {res_list[i][0]} as skill_id, {res_list[i][1]} as percent'
                else:
                    sql_vac_skill = f'{sql_vac_skill} union select {res[0][0]} as vac_id, {res_list[i][0]} as skill_id, {res_list[i][1]} as percent'
            sql_vac_skill =  f'insert into vac_to_skill(vac_id, skill_id, percent) select vac_id, skill_id, percent from ({sql_vac_skill})'
            cursor.execute(sql_vac_skill)
            conn.commit()
            cursor.close()