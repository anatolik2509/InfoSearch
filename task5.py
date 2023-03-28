import json
import math
import os
from typing import Dict, List

from nltk import word_tokenize

import task3


def read_index():
    with open('reverse_index.json')as file:
        json_index = file.readline()
        index = json.loads(json_index)
        return index


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


def read_doc_to_lemma_tf_idf() -> Dict[str, Dict[str, float]]:
    result = {}
    for file_name in os.listdir('lemma_tfidf'):
        with open('lemma_tfidf/' + file_name) as tf_idf_file:
            lines = tf_idf_file.readlines()
            result[file_name] = {}
            for line in lines:
                data = line.rstrip('\n').split(' ')
                result[file_name][data[0]] = float(data[2])
    return result


def read_lemma_to_doc_tf_idf() -> Dict[str, Dict[str, float]]:
    result = {}
    for file_name in os.listdir('lemma_tfidf'):
        with open('lemma_tfidf/' + file_name) as tf_idf_file:
            lines = tf_idf_file.readlines()
            for line in lines:
                data = line.rstrip('\n').split(' ')
                lemma_to_docs_tf_idf = result.get(data[0], {})
                lemma_to_docs_tf_idf[file_name] = float(data[2])
                result[data[0]] = lemma_to_docs_tf_idf
    return result


def calculate_doc_vector_len(doc_to_words: Dict[str, float]):
    return math.sqrt(sum(map(lambda i: i ** 2, doc_to_words.values())))


def multiply_vectors(query_vector: List[str], doc_vector: Dict[str, float], doc_vector_len: int):
    result = 0
    for token in query_vector:
        result += doc_vector.get(token, 0)
    return result / len(query_vector) / doc_vector_len


def process_query(query: str):
    print(query)
    tokens = word_tokenize(query, language='russian')
    lemmas = []
    for token in tokens:
        if token in token_to_lemma:
            lemmas.append(token_to_lemma[token])
    if len(lemmas) > 1:
        doc_set = task3.index_or(reverse_index, lemmas[0], lemmas[1])
        for lemma in lemmas:
            doc_set.update(task3.index_or(reverse_index, lemmas[0], lemma))
    else:
        doc_set = reverse_index[lemmas[0]]
    results = {}
    for doc in doc_set:
        results[doc] = multiply_vectors(lemmas, doc_to_lemma[doc], doc_lengths[doc])
    return dict(sorted(results.items(), key=lambda r: r[1], reverse=True))


docs_list = os.listdir('lemma_tfidf')
doc_to_lemma = read_doc_to_lemma_tf_idf()
lemma_to_doc = read_lemma_to_doc_tf_idf()
doc_lengths = {doc: calculate_doc_vector_len(doc_to_lemma[doc]) for doc in docs_list}
token_to_lemma = read_lemma_tokens()
reverse_index = read_index()

if __name__ == '__main__':
    test_query = 'режиссёр Шавкат'
    print(process_query(test_query))
    test_query = 'Кёнигсберг'
    print(process_query(test_query))
