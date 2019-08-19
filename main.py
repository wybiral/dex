from flask import Flask, render_template, request
from database import get_database

HOST = '127.0.0.1'
PORT = 8666

app = Flask(__name__, static_url_path='')

@app.route('/', methods=['GET'])
def root_GET():
    query = request.args.get('q', '')
    if query:
        db = get_database()
        results = db.search(query)
    else:
        results = []
    vars = {
        'query': query,
        'results': results
    }
    return render_template('index.html', **vars)

app.run(host=HOST, port=PORT, threaded=True)
