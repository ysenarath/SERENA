import json
import os.path

from serena.config import config

DATA_FOLDER = os.path.join(config['DEFAULT']['project_path'], 'resources', 'data')


def load_questions(path):
    path = os.path.join(DATA_FOLDER, path)
    with open(path, 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    processed_data = []
    for item in data:
        options = []
        is_correct_count = 0
        for i, option in enumerate(item['options']):
            is_correct = option['is_correct'].lower() == 'true'
            is_correct_count += is_correct
            options.append({
                'key': i + 1,
                'option': option['option{}'.format(i + 1)],
                'is_correct': is_correct,
            })
        assert is_correct_count > 0, 'found no correct answers, ' \
                                     'please identify the correct answer'
        assert is_correct_count == 1, 'found more than one correct answers, ' \
                                      'please note we only support only one current answer right now'
        processed_item = {'question': item['question'], 'options': options}
        processed_data.append(processed_item)
    return processed_data


questions = {
    'ALGORITHMS': load_questions('algorithm.json'),
    'CYBERSECURITY': load_questions('cybersec.json'),
    'DATABASE': load_questions('database.json'),
    'NETWORKING': load_questions('networking.json'),
}
