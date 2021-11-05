def message(text, author='bot', suggestions=None):
    if suggestions is None:
        suggestions = []
    return {
        'text': text,
        'author': author,
        'suggestions': suggestions,
    }
