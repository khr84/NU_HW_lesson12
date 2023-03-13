import search_func
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search/')
def search():
    return render_template('search.html', regions = search_req.areas_dict)

@app.route('/results/')
def results():
    return render_template('results.html')

if __name__ == '__main__':
    search_req = search_func.Search()
    app.run(debug = True)
