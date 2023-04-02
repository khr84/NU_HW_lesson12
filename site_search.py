from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect
import db_func_orm as dbfo
import db_func as dbf
import search_func
import vacancy_func as vac


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search/')
def search():
    # # обнуляем данные, если повторно пошли на поиск
    # search_req.search_vacancy = ''
    # search_req.search_strict = False
    # search_req.search_area = 'None'
    # search_req.params.pop('text', 'None')
    # search_req.params.pop('area', -1000)
    return render_template('search.html', regions=areas_dict)


@app.route('/results/')
def results():
    return render_template('results.html')


@app.route('/history/')
def history():
    hide_button = ''
    return render_template('history.html', hide_button=hide_button)


@app.route('/history/', methods=['POST'])
def history_post():
    hist_period = request.form['hist_period']
    hist_period = min(10, int(hist_period))
    now = datetime.now()
    date_end = now + timedelta(days=1)
    date_end = date_end.strftime("%Y.%m.%d")
    date_beg = now - timedelta(days=hist_period)
    date_beg = date_beg.strftime("%Y.%m.%d")
    # res_list = dbf.read_db(date_beg, date_end)
    res_list = dbfo.db_orm_read(date_beg, date_end)
    context = {'vacancy_list': res_list, 'hide_button': 'hidden'}
    return render_template('history.html', **context)


@app.route('/search/', methods=['POST'])
def search_post():
    search_req = search_func.Search()
    search_req.search_vacancy = request.form['vacancy']
    strict = request.values['strict_search']
    search_req.set_search_text(strict)
    area_str = request.form['search_area']
    if area_str != '':
        search_req.set_area(area_str)
    if search_req.search_vacancy != '':
        # делаем расчет
        search_req.search_first()
        context = {
            'vacancy': search_req.search_vacancy,
            'strict_search': search_req.search_strict,
            'search_area': search_req.search_area,
            'count_vacancy': search_req.search_count
        }
        if search_req.search_count == 0:
            context['salary'] = 'Undefine'
            context['requirements'] = {}
        else:
            search_req.search_last()
            search_req.get_result()
            context['salary'] = f'От {search_req.result["salary"]["from"]} до {search_req.result["salary"]["to"]}, определено по {search_req.result["salary"]["vacancy_with_salary"]} вакансиям с ЗП'
            context['requirements'] = search_req.result["requirements"]
            # dbf.write_db(search_req.result)
            dbfo.db_orm_check_vac(search_req.result)
            dbfo.db_orm_import_vacancy(search_req.result)
            dbfo.db_orm_import_salary(search_req.result)
            dbfo.db_orm_import_skill(search_req.result)
            dbfo.db_orm_import_vac_to_skill(search_req.result)
        return render_template('results.html', **context)
    return redirect('/search')


if __name__ == '__main__':
    hh_dict = vac.Dictionaries()
    areas_dict = hh_dict.init_areas()
    app.run(debug=True)
