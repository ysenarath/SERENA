# app.py

from flask import Flask, render_template, request, session

from serena import chat
from serena.config import config

TEMPLATE_FOLDER = config['flask']['template_folder']
STATIC_FOLDER = config['flask']['static_folder']
SECRET_KEY = config['flask']['secret_key']

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)

app.secret_key = SECRET_KEY


@app.route('/', methods=['GET', 'POST'])
def index():
    history = []
    # load status {
    if 'status' in session:
        status = session['status']
    else:
        status = {'__meta__': {'history': []}}
    # }
    history = status['__meta__']['history']
    if request.method == 'POST':
        input = request.form.get('input', None)
        # process input and get output {
        output, status = chat.process_input(input, status)
        # } update values {
        history.append({'input': input, 'output': output})
        status['__meta__']['history'] = history
        # } update session values {
        session['status'] = status
        # }
    return render_template('index.html', title='SERENA', history=history)
