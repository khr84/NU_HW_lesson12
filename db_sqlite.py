import sqlite3
conn = sqlite3.connect('sqlite.db')
cursor = conn.cursor()

# ------ table region
# cursor.execute('create table region \
#  (reg_id integer primary key, \
# reg_name text)')

# ------ table skill
# cursor.execute('create table skill \
#  (skill_id integer primary key autoincrement, \
# skill_name text unique)')

# ------ table search_vac
# cursor.execute('create table search_vac \
# (id integer primary key autoincrement, \
#  name text, \
#  count_vac integer, \
#  search_date text, \
#  region_id integer references region (reg_id),\
#  strict_search  integer,\
#  unique(name, region_id, strict_search))')

# ------ table salary
# cursor.execute('create table salary \
# (id integer references search_vac (id), \
#  low real, \
#  high real, \
#  count integer)')

#----- table vac_to_skill
# cursor.execute('create table vac_to_skill \
# (id integer primary key autoincrement, \
#  vac_id integer references search_vac (id), \
#  skill_id integer references skill (skill_id), \
#  percent  real)')

# чистим данные
# tbl_list = ['region', 'search_vac', 'skill', 'salary', 'vac_to_skill']
# for tbl in tbl_list:
#     sql = f'delete from {tbl}'
#     cursor.execute(sql)
#     conn.commit()

#удаляем таблицу
# tbl_list = ['region', 'search_vac', 'skill', 'salary', 'vac_to_skill']
# for tbl in tbl_list:
#     sql = f'drop table {tbl}'
#     cursor.execute(sql)

#смотрим данные
# tbl_list = ['search_vac', 'skill', 'salary', 'vac_to_skill']
# for tbl in tbl_list:
#     sql = f'select * from {tbl}'
#     cursor.execute(sql)
#     result = cursor.fetchall()
#     print(result)

# список таблиц
# sql_query = """SELECT * FROM region WHERE reg_id=113;"""
# cursor.execute(sql_query)
# print(cursor.fetchall())


sql = f'select v.id, v.name, v.strict_search, v.region_id, v.count_vac, s.low, s.high, s.count, v.search_date \
      from search_vac v join salary s on s.id = v.id'
cursor.execute(sql)
result_list = cursor.fetchall()
print(result_list)