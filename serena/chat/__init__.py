from serena.chat import elements as el


def process_input(input, status):
    input_text = input['text']
    output = el.message(text='User Says: {}'.format(input_text))
    return output, status
