from sqlalchemy import create_engine
from sqlalchemy.sql import insert
from sqlalchemy.orm import sessionmaker
from db_sqlite_orm import DBRegion, DBVacancy, DBSalary, vac_to_skill, DBSkill
from datetime import datetime


def get_vac(vac_dict):
    engine = create_engine('sqlite:///sqlite_orm.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    db_reg_id = list(session.query(DBRegion.reg_id).filter(DBRegion.reg_name == vac_dict['area']))
    db_vac_id = list(session.query(DBVacancy.id).filter(DBVacancy.name == vac_dict['keywords'],
                                                  DBVacancy.region_id == db_reg_id[0].reg_id,
                                                  DBVacancy.strict_search == vac_dict['search_strict']))
    vac_id = -1 if len(db_vac_id) == 0 else db_vac_id[0].id
    return(vac_id, db_reg_id[0].reg_id)


def db_orm_check_vac(vac_dict):
    # проверяем есть ли уже такая вакансия
    engine = create_engine('sqlite:///sqlite_orm.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    vac_data = get_vac(vac_dict)
    if vac_data[0] != -1:
        session.query(DBVacancy).filter(DBVacancy.id == vac_data[0]).delete()
        session.query(DBSalary).filter(DBSalary.id == vac_data[0]).delete()
        session.query(vac_to_skill).filter(vac_to_skill.c.vac_id == vac_data[0]).delete()
        session.commit()


def db_orm_import_region(region_dict):
    if len(region_dict) == 0:
        pass
    else:
        # Заполняем DBRegion
        engine = create_engine('sqlite:///sqlite_orm.db', echo=True)
        Session = sessionmaker(bind=engine)
        session = Session()
        region_list = list(map(lambda x: (x[0], int(x[1])), region_dict.items()))
        region_list.append(('None', -1000))
        db_regions = session.query(DBRegion.reg_name, DBRegion.reg_id)
        db_region_list = []
        for db_region in db_regions:
            db_region_list.append((db_region.reg_name, db_region.reg_id))
        for region in region_list:
            if region not in db_region_list:
                # проверяем есть ли такой id
                result = session.query(DBRegion).filter(DBRegion.reg_id == region[1]).first()
                if result:  # если id есть, то апдейтим наименование
                    session.query(DBRegion).filter(DBRegion.reg_name == region[1]).update({"reg_name": region[0]})
                else:  # если id нет, то добавляем сроку
                    session.add(DBRegion(region[1], region[0]))
        session.commit()


def db_orm_import_vacancy(vac_dict):
    # Заполняем DBVacancy
    engine = create_engine('sqlite:///sqlite_orm.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    now = datetime.now()
    current_time = now.strftime("%Y.%m.%d %H:%M:%S")
    reg_id = session.query(DBRegion.reg_id).filter(DBRegion.reg_name == vac_dict['area'])
    strict_search = 1 if vac_dict['search_strict'] else 0
    session.add(DBVacancy(vac_dict['keywords'], vac_dict['count'], current_time, reg_id[0].reg_id, strict_search))
    session.commit()


def db_orm_import_salary(vac_dict):
    # Заполняем DBSalary
    engine = create_engine('sqlite:///sqlite_orm.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    vac_data = get_vac(vac_dict)
    session.add(DBSalary(vac_data[0], vac_dict['salary']['from'], vac_dict['salary']['to'], vac_dict['salary']['vacancy_with_salary']))
    session.commit()


def db_orm_import_skill(vac_dict):
    engine = create_engine('sqlite:///sqlite_orm.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    skill_list = vac_dict['requirements']
    db_skill_list = session.query(DBSkill.skill_name)
    db_skill_list = list(map(lambda x: x[0], list(db_skill_list)))
    for i in range(len(skill_list)-1):
        print(skill_list[i]['name'])
        if skill_list[i]['name'] not in db_skill_list:
            print('add')
            session.add(DBSkill(skill_list[i]['name']))
        else:
            print('pass')
            continue
    session.commit()


def db_orm_import_vac_to_skill(vac_dict):
    engine = create_engine('sqlite:///sqlite_orm.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    vac_data = get_vac(vac_dict)
    skill_list = vac_dict['requirements']
    for i in range(len(skill_list) - 1):
        skill_id = session.query(DBSkill.skill_id).filter(DBSkill.skill_name == skill_list[i]['name'])
        sql = insert(vac_to_skill).values(vac_id=vac_data[0], skill_id=skill_id[0].skill_id, percent=skill_list[i]['percent'])
        with engine.connect() as conn:
            conn.execute(sql)
            conn.commit()


def db_orm_read(date_beg, date_end):
    engine = create_engine('sqlite:///sqlite_orm.db', echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    vac_list = []
    result_list = list(session.query(DBVacancy.id, DBVacancy.name, DBVacancy.strict_search, DBVacancy.count_vac, DBRegion.reg_name,
                          DBSalary.low, DBSalary.high, DBSalary.count, DBVacancy.search_date). \
                            join(DBRegion, DBVacancy.region_id == DBRegion.reg_id). \
                            join(DBSalary, DBVacancy.id == DBSalary.vac_id). \
                            filter(DBVacancy.search_date >= date_beg, DBVacancy.search_date < date_end))
    result_list.sort(key=lambda x: x[-1], reverse=True)
    for res in result_list:
        skill_list = list(session.query(DBSkill.skill_name, vac_to_skill.c.percent).\
                                 join(vac_to_skill, vac_to_skill.c.skill_id == DBSkill.skill_id). \
                                 filter(vac_to_skill.c.vac_id == res[0]))
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
    return vac_list


if __name__ == '__main__':
    print(1)
