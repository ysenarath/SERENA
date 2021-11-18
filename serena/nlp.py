import nltk

nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')


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
