# app.py

from flask import Flask, render_template

from serena import agent
from serena.config import config

TEMPLATE_FOLDER = config['flask']['template_folder']
STATIC_FOLDER = config['flask']['static_folder']

app = Flask(__name__, template_folder=TEMPLATE_FOLDER, static_folder=STATIC_FOLDER)


@app.route("/")
def index():
    input = ''
    history = []
    status = {'__meta__': {'history': history}}
    output, status = agent.process_input(input, status)
    history.append({'input': input, 'status': status, 'output': output})
    status['__meta__']['history'] = history
    return render_template('index.html', title='SERENA')
