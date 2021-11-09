# app.py
import collections

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
    if 'state' in session:
        state = session['state']  # load state
    else:
        state = {'__meta__': {'history': []}}
    history = state['__meta__']['history']
    input = None
    if request.method == 'POST':
        input = request.form.get('input', None)
        if input is not None and len(input.strip()) != 0:
            input = chat.message(input, author='user')
            history.append(input)
    elif len(history) == 0:
        input = chat.message(None, author='user')
    if input is not None:
        output, state = chat.process_input(input, state)  # process input and get output
        if not isinstance(output, collections.Sequence):
            output = [output]
        history += output
        state['__meta__']['history'] = history  # update history
        session['state'] = state  # update state
    return render_template('index.html', title='SERENA', history=history)
