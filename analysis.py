import pandas as pd
import numpy as np
import pymorphy2
import re
from functools import reduce
from collections import Counter
import math
from nltk.corpus import stopwords
from scipy.spatial.distance import pdist, squareform


morph = pymorphy2.MorphAnalyzer()
regex = '\w+'


def get_words(*args):
    array = list(map(lambda x: re.findall(regex, str(x)), args))
    return reduce((lambda x, y: x + y), array)


def get_normal_forms(words):
    return list(map(lambda x: morph.parse(x.lower())[0].normal_form, words))


def compute_tfidf(corpus):
    def compute_tf(text):
        tf_text = Counter(text)
        for i in tf_text:
            tf_text[i] = tf_text[i]/float(len(text))
        return tf_text

    def compute_idf(word, corpus):
        return math.log10(len(corpus)/sum([1.0 for i in corpus if word in i]))

    documents_list = []
    for text in corpus:
        tf_idf_dictionary = {}
        computed_tf = compute_tf(text)
    for word in computed_tf:
        tf_idf_dictionary[word] = computed_tf[word] * compute_idf(word, corpus)
        documents_list.append(tf_idf_dictionary)
    return documents_list


manual_services = {'принтер': ['принтер', 'мфу', 'тонер', 'картридж'],
                   'тула': ['тула'],
                   'аис мфц': ['аис мфц'],
                   'жкх': ['жкх'],
                   'кнд': ['тор кнд', 'кнд', 'ас кнд'],
                   'vpn': ['vpn'],
                   'глонасс': ['глонасс']}
manual_services_values = []
for x in list(manual_services.values()):
    manual_services_values += x

keywords_stat = {}
for k in manual_services.keys():
    keywords_stat[k] = 0

df = pd.read_csv('report.csv', sep=';', encoding='ansi')

# words = []
# for idx, row in df.iterrows():
#     words += get_words(row['artbody'])

# words = get_normal_forms(list(set(words)))
# words = list(set(words))
# nf_words = get_normal_forms(words)
# counts = Counter(nf_words)

def request_keywords_stat():
    for idx, row in df.iterrows():
        words = []
        if pd.notna(row['artsubject']):
            words += get_words(row['artsubject'])
        if pd.notna(row['artbody']):
            words += get_words(row['artbody'])
        sentence = ' '.join(words).lower()
        words = get_normal_forms(words)
        nf_sentence = ' '.join(words)
    # =============================================================================
    #     if 'кнд' in sentence or 'кнд' in nf_sentence:
    #         print(df.T[idx]['tn'])
    #     else:
    #         continue
    # =============================================================================
        for key in manual_services.keys():
            for keyword in manual_services[key]:
                if keyword in sentence or keyword in nf_sentence:
                    keywords_stat[key] += 1
                    break
        if idx % 100 == 0:
            print(idx)

    print(keywords_stat)


documents = list(df.tn)


total_words = []
doc_words = []
for index, row in df.iterrows():
    words = []
    if pd.notna(row['artsubject']):
        words += get_words(row['artsubject'])
    if pd.notna(row['artbody']):
        words += get_words(row['artbody'])
    sentence = ' '.join(words).lower()
    words = get_normal_forms(words)
    nf_sentence = ' '.join(words)
    # row_words = re.findall(regex, row['artbody'].lower()) # .astype(str)
    # sentence = ' '.join(row_words)
    # row_words = sentence.split()
    # normalized_words = [x for x in get_normal_forms(row_words) if x != '']

    # words += [x for x in normalized_words if x not in stopwords.words('russian')]
    total_words += words
    doc_words.append({'ticket': row.tn, 'words': words})

raise 'OMG'
# Delete duplicates
total_words = list(set(total_words))
print(len(total_words))

count_df = pd.DataFrame(0, index=documents, columns=total_words)
for row in doc_words:
    for word in row['words']:
        count_df.T[row['ticket']][word] += 1


tf = pd.DataFrame(0.0, index=documents, columns=total_words)
for row in doc_words:
    for word in row['words']:
        tf.T[row['ticket']][word] = count_df.T[row['ticket']][word] / len(row['words'])

idf = {}
for word in total_words:
    count = 0
    for row in doc_words:
        if word in row['words']:
            count += 1
    idf.update({word: np.log(len(doc_words) / count)})

# Compute TFxIDF
tf_idf = pd.DataFrame(0.0, index=documents, columns=total_words)
for row in doc_words:
    for word in row['words']:
        tf_idf.T[row['ticket']][word] = tf.T[row['ticket']][word] * idf[word]

# mtx_similarity = squareform(pdist(tf_idf, 'cosine'))
