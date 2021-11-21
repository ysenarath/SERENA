import enum
import random

import nltk

from serena import db

nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('punkt')


def get_names(text):
    chunked = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(text)))
    continuous_chunk = []
    current_chunk = []
    current_chunk_label = None
    for i in chunked:
        if type(i) == nltk.tree.Tree:
            if current_chunk_label is None:
                current_chunk_label = i.label()
            if current_chunk_label == 'PERSON':
                current_chunk.append(' '.join([token for token, pos in i.leaves()]))
        elif current_chunk:
            named_entity = ' '.join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
                current_chunk_label = None
        else:
            continue
    if current_chunk:
        named_entity = ' '.join(current_chunk)
        if named_entity not in continuous_chunk:
            continuous_chunk.append(named_entity)
    return continuous_chunk


def message(text=None, author='bot', suggestions=None, options=None, report=None, type='default'):
    if suggestions is None:
        suggestions = []
    if options is None:
        options = []
    type_of_message = type
    if type_of_message is None:
        type_of_message = 'default'
    return {
        'text': text,
        'author': author,
        'suggestions': suggestions,
        'options': options,
        'report': report,
        'type': type_of_message,
    }


@enum.unique
class StateValue(enum.IntEnum):
    START = 0
    ASK_NAME = 1
    ASK_TEST_TYPE = 2
    ASK_QUESTION = 3
    SHOW_REPORT = 6
    SHOW_REPORT_EXT = 7
    ASK_ANOTHER = 8


def get_test_type(text):
    """

    :param text:
    :return: one of (ALGORITHMS, CYBERSECURITY, DATABASE, NETWORKING)
    """
    text = text.lower()
    test_type = None
    if 'algo' in text:
        test_type = 'ALGORITHMS'
    elif ('cyber' in text) or ('security' in text):
        test_type = 'CYBERSECURITY'
    elif 'network' in text:
        test_type = 'NETWORKING'
    elif ('database' in text) or ('db' in text):
        test_type = 'DATABASE'
    return test_type


def get_answer_index(text, options):
    answer_index = None
    options = {o['key']: i for i, o in enumerate(options)}
    try:
        answer_key = int(text)
        if answer_key in options:
            answer_index = options[answer_key]
    except ValueError as e:
        pass
    return answer_index


def get_is_true(input_text):
    if input_text.lower() in ['yes', 'y', 'true', 'yeah', 'please']:
        return True
    elif input_text.lower() in ['no', 'n', 'false', 'nah', 'don\'t', 'do not', 'can\'t', 'later', 'may be later']:
        return False
    return None


def get_username(input_text, username):
    names_in_text = get_names(input_text)
    if names_in_text is not None and len(names_in_text) > 0:
        username = names_in_text[0]
    return username


def process_input(input, state):
    input_text = input.get('text', None)
    state_value = state.get('value', StateValue.START)
    username = state.get('username', None)
    current_test = state.get('current_test', None)
    current_report = state.get('current_report', None)
    output = []
    if state_value == StateValue.START:
        if username is None:
            output += [
                message(text='Welcome! I’m Serena, here to help you to prepare for exams.'),
                message(text='What is your name?', suggestions=['Skip'])
            ]
            state_value = StateValue.ASK_NAME
        else:
            output += [
                message(text='Hi {}, nice to meet you again!'.format(username)),
                message(text='What do you like to learn now?', suggestions=[
                    'Algorithms', 'Cybersecurity', 'Database', 'Networking',
                ]),
            ]
            state_value = StateValue.ASK_TEST_TYPE
    elif state_value == StateValue.ASK_NAME:
        if 'skip' in input_text.lower():
            username = 'Guest'
            output += [
                message(text='Which subject do you want to learn today?', suggestions=[
                    'Algorithms', 'Cybersecurity', 'Database', 'Networking',
                ]),
            ]
            state_value = StateValue.ASK_TEST_TYPE
        else:
            username = get_username(input_text, username)
            if username is None:
                output += [
                    message(text='Sorry, I didn\'t catch your name.'),
                    message(text='Could you please enter your name again?'),
                ]
            else:
                output += [
                    message(text='Nice to meet you {}'.format(username)),
                    message(text='Which subject do you want to learn today?', suggestions=[
                        'Algorithms', 'Cybersecurity', 'Database', 'Networking',
                    ]),
                ]
                state_value = StateValue.ASK_TEST_TYPE
    elif state_value == StateValue.ASK_TEST_TYPE:
        test_type = get_test_type(input_text)
        if test_type is None:
            output += [
                message(text='Sorry, I couldn\'t catch the test type.'),
                message(text='can you try again?', suggestions=[
                    'Algorithms', 'Cybersecurity', 'Database', 'Networking',
                ]),
            ]
        else:
            # create new test
            current_question_index = 0
            current_test = {
                'questions': random.sample(db.questions[test_type], 5),
                'current_index': current_question_index
            }
            question = current_test['questions'][current_question_index]
            output += [
                message(text='Sounds good, please provide answers to following questions on {}.'.format(
                    test_type.lower()
                )),
                message(text=question['question'], options=question['options']),
            ]
            state_value = StateValue.ASK_QUESTION
    elif state_value == StateValue.ASK_QUESTION:
        if current_test is not None:
            current_question_index = current_test['current_index']
            previous_question = current_test['questions'][current_question_index]
            answer_idx = get_answer_index(input_text, options=previous_question['options'])
            if answer_idx is not None:
                previous_question['options'][answer_idx]['is_answer'] = True
                if previous_question['options'][answer_idx]['is_correct']:
                    message_text = 'Your answer is correct!'
                else:
                    message_text = 'It looks like your answer is incorrect.'
                output += [
                    # show answer to previous question
                    message(text=message_text, options=previous_question['options'], type='answer')
                ]
                if current_test['current_index'] < len(current_test['questions']) - 1:
                    current_test['current_index'] = current_question_index + 1
                    question = current_test['questions'][current_test['current_index']]
                    output += [
                        # ask next question
                        message(text=question['question'], options=question['options'])
                    ]
                    state_value = StateValue.ASK_QUESTION
                else:
                    score = 0
                    questions = []
                    for question in current_test['questions']:
                        correct_answer = None
                        selected_answer = None
                        is_correct = False
                        for option in question['options']:
                            if 'is_answer' in option and option['is_answer']:
                                selected_answer = option['option']
                            if option['is_correct'] and 'is_answer' in option and option['is_answer']:
                                is_correct = True
                                correct_answer = option['option']
                        if is_correct:
                            score += 1
                        questions.append({
                            'question': question['question'],
                            'correct_answer': correct_answer,
                            'selected_answer': selected_answer,
                        })
                    current_report = {'score': score, 'questions': questions}
                    if len(current_report['questions']) != 0:
                        current_report['percentage'] = current_report['score'] * 100 / len(current_report['questions'])
                    else:
                        current_report['percentage'] = 0
                    if current_report['percentage'] >= 80:
                        title = 'Congratulations 🎉'
                    elif current_report['percentage'] >= 40:
                        title = 'Good Work!'
                    else:
                        title = 'Let\'s try again!'
                    current_report['title'] = title
                    subtitle = 'Your score is {}.'.format(score)
                    current_report['subtitle'] = subtitle
                    output += [
                        # show minimal report and ask if she wants to continue
                        message(report=current_report, type='report'),
                        message(text='Do you want to review?', suggestions=['Yes', 'No']),
                    ]
                    current_test = None
                    state_value = StateValue.SHOW_REPORT
            else:
                output += [
                    message(text='Sorry, I did\'t understand your answer. Here is the question again.'),
                    message(text=previous_question['question'], options=previous_question['options']),
                ]
                state_value = StateValue.ASK_QUESTION
        else:
            output += [
                message(text='We couldn\'t create a test for you now. '
                             'Please try again later.'),
                message(text='Do you want to select another test?', suggestions=['Yes', 'No']),
            ]
            state_value = StateValue.ASK_ANOTHER
    elif state_value == StateValue.SHOW_REPORT:
        if 'more' in input_text or get_is_true(input_text):
            output += [
                # show extended report and ask again if she wants to continue
                message(report=current_report, type='extended_report'),
            ]
            current_report = None
        output += [
            # ask if she wants to continue
            message(text='Do you want to select another test?', suggestions=['Yes', 'No'])
        ]
        state_value = StateValue.ASK_ANOTHER
    elif state_value == StateValue.ASK_ANOTHER:
        is_true = get_is_true(input_text)
        if is_true is not None:
            if is_true:
                output += [
                    message(text='Which subject do you want to learn now?', suggestions=[
                        'Algorithms', 'Cybersecurity', 'Database', 'Networking',
                    ])
                ]
                state_value = StateValue.ASK_TEST_TYPE
            else:
                output += [
                    message(text='Thank you, please come back again!'),
                ]
                state_value = StateValue.ASK_NAME
        else:
            output += [
                message(text='Sorry, can you please repeat, I did not understand?', suggestions=['Yes', 'No']),
            ]
    state['value'] = state_value
    state['username'] = username
    state['current_test'] = current_test
    state['current_report'] = current_report
    return output, state
