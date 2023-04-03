import sqlite3
import vacancy_func as vac
from datetime import datetime
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


def write_db(vac_dict):
    # ==================insert regions
    cursor = conn.cursor()
    hh_dict = vac.Dictionaries()
    areas_dict = hh_dict.init_areas()
    region_list = list(areas_dict.items())
    # добавим дефолтное значение если регион не указан
    region_list.append(('None', -1000))
    for i in range(len(region_list)):
        sql_reg = f"""select {region_list[i][1]} as id,\'{region_list[i][0]}\' as name"""
        sql_reg = f"""insert into region(reg_id, reg_name) select id, name from ({sql_reg}) t \
                    left join region r on r.reg_name = t.name where r.reg_name is null"""
        cursor.execute(sql_reg)
        conn.commit()
    # ==================insert vacancy
    vacancy = f"\"{vac_dict['keywords']}\""
    region = f"{vac_dict['area']}"
    region_id = areas_dict.get(region, -1000)
    strict = 1 if vac_dict['search_strict'] else 0
    sql_vac = f"""select id from search_vac where name = {vacancy} and region_id = {region_id} and strict_search = {strict}"""
    cursor.execute(sql_vac)
    res = cursor.fetchall()
    # удаление текущих значений если такая вакансия уже есть
    if res:
        sql_vac = f"""delete from vac_to_skill where vac_id = {res[0][0]}"""
        cursor.execute(sql_vac)
        conn.commit()
        sql_vac = f"""delete from salary where id = {res[0][0]}"""
        cursor.execute(sql_vac)
        conn.commit()
        sql_vac = f"""delete from search_vac where id = {res[0][0]}"""
        cursor.execute(sql_vac)
        conn.commit()
    # вставка новых значений
    now = datetime.now()
    current_time = now.strftime("%Y.%m.%d %H:%M:%S")
    sql_vac = f"""select {vacancy} as name, {vac_dict['count']} as count, \'{current_time}\' as search_date, {region_id} as reg_id, {strict} as strict"""
    sql_vac = f"""insert into search_vac(name, count_vac, search_date, region_id, strict_search) select * from ({sql_vac})"""
    cursor.execute(sql_vac)
    conn.commit()
    # ====================insert salary
    sql_vac = f"""select id from search_vac where name = {vacancy} and region_id = {region_id} and strict_search = {strict}"""
    cursor.execute(sql_vac)
    res = cursor.fetchall()
    sql_vac = f"""select {res[0][0]} as id, {vac_dict['salary']['from']} as low, {vac_dict['salary']['to']} as high, \
                {vac_dict['salary']['vacancy_with_salary']} as count"""
    sql_vac = f"""insert into salary select id, low, high, count from ({sql_vac})"""
    cursor.execute(sql_vac)
    conn.commit()
    # ==================insert skills
    sql_skill = ''
    for i in range(len(vac_dict['requirements'])-1):  # (-1): убираем other
        skill = vac_dict['requirements'][i]['name']
        percent = vac_dict['requirements'][i]['percent']
        if i == 0:
            sql_skill = f"""select \'{skill}\' as name, {percent} as percent"""
        else:
            sql_skill = f"""{sql_skill} union select \'{skill}\' as name, {percent} as percent"""
    sql_skill_ins = f"""insert into skill(skill_name) select name from ({sql_skill}) t \
                    left join skill s on s.skill_name = t.name where s.skill_name is null"""
    cursor.execute(sql_skill_ins)
    conn.commit()
    # ====================insert vac_to_skill
    sql_vac_skill = f"""select skill_id, t.percent  from skill s join ({sql_skill}) t on t.name = s.skill_name"""
    cursor.execute(sql_vac_skill)
    res_list = cursor.fetchall()
    for i in range(len(res_list)):
        if i == 0:
            sql_vac_skill = f'select {res[0][0]} as vac_id, {res_list[i][0]} as skill_id, {res_list[i][1]} as percent'
        else:
            sql_vac_skill = f'{sql_vac_skill} union select {res[0][0]} as vac_id, {res_list[i][0]} as skill_id, {res_list[i][1]} as percent'
    sql_vac_skill = f'insert into vac_to_skill(vac_id, skill_id, percent) select vac_id, skill_id, percent from ({sql_vac_skill})'
    cursor.execute(sql_vac_skill)
    conn.commit()
    cursor.close()
