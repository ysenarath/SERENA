# app.py
import collections

import flask
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
        input_text = request.form.get('input', None)
        if input_text is not None and len(input_text.strip()) != 0:
            input = chat.message(input_text, author='user')
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
    return render_template('index.html', title='SERENA', history=history, state=state)


@app.route('/logout')
def logout():
    session.pop('state')
    return flask.redirect(flask.url_for('index'))
