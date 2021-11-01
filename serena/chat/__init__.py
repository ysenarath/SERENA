from serena.chat import elements as el


def process_input(input, status):
    output = el.message(text='User Says: {}'.format(input))
    return output, status
