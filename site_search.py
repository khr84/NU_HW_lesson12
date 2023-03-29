import search_func
import time
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search/')
def search():
    # обнуляем данные, если повторно пошли на поиск
    search_req.search_vacancy = ''
    search_req.search_strict = False
    search_req.search_area = 'None'
    search_req.params.pop('text', 'None')
    search_req.params.pop('area', -1000)
    return render_template('search.html', regions = search_req.areas_dict)

@app.route('/results/')
def results():
    return render_template('results.html')

@app.route('/search/', methods=['POST'])
def search_post():
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
            'vacancy':search_req.search_vacancy,
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


        return render_template('results.html', **context)
    return redirect('/search')

if __name__ == '__main__':
    search_req = search_func.Search()
    app.run(debug = True)
