from typing import Dict, List, Set
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
import re
import json


def prepare_token(token):
    return re.sub("[^а-яА-ЯёЁ-]", '', token)


def read_lemma_tokens() -> Dict[str, str]:
    lemmas = {}
    with open('lemma_tokens.txt') as lemma_file:
        lines = lemma_file.readlines()
        for line in lines:
            line = line.rstrip('\n')
            words = line.split(' ')
            for word in words:
                lemmas[word] = words[0]
    return lemmas


def tokenize_page(page_text: str) -> Set[str]:
    tokens = word_tokenize(page_text, language='russian')
    uniq_filtered_tokens = set()
    stop_words = stopwords.words('russian')
    # Обрабатываем и фильтруем токены
    for token in tokens:
        prepared = prepare_token(token)
        if prepared == '':
            continue
        if prepared in stop_words:
            continue
        uniq_filtered_tokens.add(prepared)
    return uniq_filtered_tokens


def build_index():
    reverse_index = {}
    lemma_tokens = read_lemma_tokens()
    for text_page in os.listdir('plain_pages/'):
        file = open('plain_pages/' + text_page)
        lines = file.readlines()
        tokens = tokenize_page('\n'.join(lines))
        for token in tokens:
            lemma = lemma_tokens.get(token, None)
            if lemma is None:
                continue
            if lemma not in reverse_index:
                reverse_index[lemma] = set()
            reverse_index[lemma].add(text_page)
        file.close()
    for key in reverse_index.keys():
        reverse_index[key] = list(reverse_index[key])
    json_reverse_index = json.dumps(reverse_index, ensure_ascii=False)
    with open('reverse_index.json', 'w+') as index_file:
        index_file.write(json_reverse_index)


def read_index():
    with open('reverse_index.json')as file:
        json_index = file.readline()
        index = json.loads(json_index)
        return index


def index_and(index, word, another_word):
    word_docs = index.get(word, [])
    another_word_docs = index.get(another_word, [])
    word_docs = set(word_docs)
    another_word_docs = set(another_word_docs)
    return word_docs.intersection(another_word_docs)


def index_or(index, word, another_word):
    word_docs = index.get(word, [])
    another_word_docs = index.get(another_word, [])
    word_docs = set(word_docs)
    another_word_docs = set(another_word_docs)
    word_docs.update(another_word_docs)
    return word_docs


def index_not(index, word):
    all_docs = set(os.listdir('plain_pages/'))
    word_docs = set(index.get(word, []))
    return all_docs - word_docs


if __name__ == '__main__':
    build_index()
    reversed_index = read_index()
    token_to_lemma = read_lemma_tokens()
    print(index_and(reversed_index, token_to_lemma['режиссёр'], token_to_lemma['фильм']))
    print(index_or(reversed_index, token_to_lemma['холодный'], token_to_lemma['салихович']))
    print(index_not(reversed_index, token_to_lemma['холодный']))
