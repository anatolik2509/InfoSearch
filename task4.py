import json
import math
import os
import re
from typing import List, Dict

from nltk import word_tokenize
from nltk.corpus import stopwords


def prepare_token(token):
    return re.sub("[^а-яА-ЯёЁ-]", '', token)


def tokenize_page(page_text: str) -> List[str]:
    tokens = word_tokenize(page_text, language='russian')
    filtered_tokens = list()
    stop_words = stopwords.words('russian')
    # Обрабатываем и фильтруем токены
    for token in tokens:
        prepared = prepare_token(token)
        if prepared == '':
            continue
        if prepared in stop_words:
            continue
        filtered_tokens.append(prepared)
    return filtered_tokens


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


def read_index():
    with open('reverse_index.json')as file:
        json_index = file.readline()
        index = json.loads(json_index)
        return index


def get_all_docs() -> List[str]:
    return os.listdir('plain_pages/')


def get_doc_to_tokens() -> Dict[str, List[str]]:
    result = {}
    for text_page in get_all_docs():
        file = open('plain_pages/' + text_page)
        lines = file.readlines()
        tokens = tokenize_page('\n'.join(lines))
        result[text_page] = tokens
    return result


def get_tokens() -> List[str]:
    with open('tokens.txt') as token_file:
        token_list = token_file.readlines()
        token_list = list(map(lambda s: s.rstrip('\n'), token_list))
        return token_list


def calculate_tf(token: str, docs: Dict[str, List[str]]) -> Dict[str, float]:
    result = {}
    for doc, text in docs.items():
        if len(text) == 0:
            continue
        if token not in text:
            continue
        entries = 0.0
        for word in text:
            if word == token:
                entries += 1
        result[doc] = entries / len(text)
    return result


def calculate_lemma_tf(lemma: str, docs: Dict[str, List[str]]) -> Dict[str, float]:
    result = {}
    for doc, text in docs.items():
        if len(text) == 0:
            continue
        if lemma not in text:
            continue
        entries = 0.0
        for word in text:
            if word == lemma:
                entries += 1
        result[doc] = entries / len(text)
    return result


def calculate_idf(token: str, docs: Dict[str, List[str]]) -> float:
    docs_count = 0
    for doc, text in docs.items():
        if token in text:
            docs_count += 1
    if docs_count == 0:
        print(f'No token in docs: {token}')
        return 0
    return math.log(len(docs) / docs_count)


def calculate_lemma_idf(lemma: str, docs_count: int, index: Dict[str, List[str]]) -> float:
    return math.log(docs_count / len(index[lemma]))


if __name__ == '__main__':
    token_to_lemma = read_lemma_tokens()
    doc_to_token = get_doc_to_tokens()
    tokens = get_tokens()
    token_to_tf = {}
    token_to_idf = {}
    index = read_index()
    print(token_to_lemma)
    for token in tokens:
        token_to_tf[token] = calculate_tf(token, doc_to_token)
        token_to_idf[token] = calculate_idf(token, doc_to_token)
    for page in get_all_docs():
        with open('tfidf/' + page, "w+") as tfidf_file:
            for token in tokens:
                if page not in token_to_tf[token]:
                    continue
                tfidf_file.write(f'{token} {token_to_idf[token]} {token_to_idf[token] * token_to_tf[token][page]}\n')
    for doc, text in doc_to_token.items():
        doc_to_token[doc] = list(map(lambda token: token_to_lemma[token], text))

    lemma_to_tf = {}
    lemma_to_idf = {}

    for token in tokens:
        lemma = token_to_lemma[token]
        lemma_to_tf[lemma] = calculate_lemma_tf(token_to_lemma[token], doc_to_token)
        lemma_to_idf[lemma] = calculate_lemma_idf(token_to_lemma[token], len(doc_to_token), index)
    for page in get_all_docs():
        with open('lemma_tfidf/' + page, "w+") as tfidf_file:
            for token in tokens:
                lemma = token_to_lemma[token]
                if page not in lemma_to_tf[lemma]:
                    continue
                tfidf_file.write(f'{lemma} {lemma_to_idf[lemma]} {lemma_to_idf[lemma] * lemma_to_tf[lemma][page]}\n')


