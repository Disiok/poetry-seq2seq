#! /usr/bin/env python
#-*- coding:utf-8 -*-

import codecs
import os
import random

import numpy as np

from cnt_words import get_pop_quatrains
from rank_words import get_word_ranks
from segment import Segmenter
from utils import DATA_PROCESSED_DIR, embed_w2v, apply_one_hot, apply_sparse, pad_to, SEP_TOKEN, PAD_TOKEN
from vocab import ch2int, VOCAB_SIZE, sentence_to_ints
from word2vec import get_word_embedding

train_path = os.path.join(DATA_PROCESSED_DIR, 'train.txt')
kw_train_path = os.path.join(DATA_PROCESSED_DIR, 'kw_train.txt')


def fill_np_matrix(vects, batch_size, value):
    max_len = max(len(vect) for vect in vects)
    res = np.full([batch_size, max_len], value, dtype=np.int32)
    for row, vect in enumerate(vects):
        res[row, :len(vect)] = vect
    return res


def fill_np_array(vect, batch_size, value):
    result = np.full([batch_size], value, dtype=np.int32)
    result[:len(vect)] = vect
    return result


def _gen_train_data():
    segmenter = Segmenter()
    poems = get_pop_quatrains()
    random.shuffle(poems)
    ranks = get_word_ranks()
    print "Generating training data ..."
    data = []
    kw_data = []
    for idx, poem in enumerate(poems):
        sentences = poem['sentences']
        if len(sentences) == 4:
            flag = True
            lines = u''
            rows = []
            kw_row = []
            for sentence in sentences:
                rows.append([sentence])
                segs = filter(lambda seg: seg in ranks, segmenter.segment(sentence))
                if 0 == len(segs):
                    flag = False
                    break
                keyword = reduce(lambda x,y: x if ranks[x] < ranks[y] else y, segs)
                kw_row.append(keyword)
                rows[-1].append(keyword)
            if flag:
                data.extend(rows)
                kw_data.append(kw_row)
        if 0 == (idx+1)%2000:
            print "[Training Data] %d/%d poems are processed." %(idx+1, len(poems))
    with codecs.open(train_path, 'w', 'utf-8') as fout:
        for row in data:
            fout.write('\t'.join(row)+'\n')
    with codecs.open(kw_train_path, 'w', 'utf-8') as fout:
        for kw_row in kw_data:
            fout.write('\t'.join(kw_row)+'\n')
    print "Training data is generated."


def get_train_data():
    if not os.path.exists(train_path):
        _gen_train_data()
    data = []
    with codecs.open(train_path, 'r', 'utf-8') as fin:
        line = fin.readline()
        while line:
            toks = line.strip().split('\t')
            data.append({'sentence':toks[0], 'keyword':toks[1]})
            line = fin.readline()
    return data

def get_keras_train_data():
    train_data = get_train_data()
    
    X_train = []
    Y_train = []
    for idx in xrange(len(train_data)):
        line_number = idx % 4
        
        keyword = train_data[idx]['keyword']
        current_sentence = train_data[idx]['sentence']
        previous_sentences = ''.join([train_data[idx - i]['sentence'] for i in range(line_number, 0, -1)])
        
        X_entry = pad_to([ch2int[ch] for ch in (keyword + previous_sentences)], 26, 5999)
        Y_entry = pad_to([ch2int[ch] for ch in current_sentence], 8, 5999)
        
        X_train.append(X_entry)
        Y_train.append(Y_entry)
        
    return X_train, Y_train

def gen_keras_one_hot_train_data(batch_size=64):
    print 'Preparing data'
    embedding = get_word_embedding(128)
    X_train, Y_train = get_keras_train_data()

    X_train_embedded = embed_w2v(embedding, X_train)
    Y_train_one_hot = apply_one_hot(Y_train)

    n_samples = len(X_train)


    print 'Data preparation completed'
    i = 0 
    while True:

        yield np.array(X_train_embedded[i: i + batch_size]), np.array(Y_train_one_hot[i: i + batch_size])

        if i + batch_size > n_samples:
            i = 0
        else:
            i += batch_size


def gen_keras_sparse_train_data(batch_size=64):
    print 'Preparing data'
    embedding = get_word_embedding(128)
    X_train, Y_train = get_keras_train_data()

    X_train_embedded = embed_w2v(embedding, X_train)
    Y_train_one_hot = apply_sparse(Y_train)

    n_samples = len(X_train)


    print 'Data preparation completed'
    i = 0 
    while True:

        yield np.array(X_train_embedded[i: i + batch_size]), np.array(Y_train_one_hot[i: i + batch_size])

        if i + batch_size > n_samples:
            i = 0
        else:
            i += batch_size


def gen_keras_train_data(batch_size=64):
    print 'Preparing data'
    embedding = get_word_embedding(128)
    X_train, Y_train = get_keras_train_data()

    X_train_embedded = embed_w2v(embedding, X_train)
    Y_train_embedded = embed_w2v(embedding, Y_train)

    n_samples = len(X_train)


    print 'Data preparation completed'
    i = 0 
    while True:

        yield np.array(X_train_embedded[i: i + batch_size]), np.array(Y_train_embedded[i: i + batch_size])

        if i + batch_size > n_samples:
            i = 0
        else:
            i += batch_size


def get_kw_train_data():
    if not os.path.exists(kw_train_path):
        _gen_train_data()
    data = []
    with codecs.open(kw_train_path, 'r', 'utf-8') as fin:
        line = fin.readline()
        while line:
            data.append(line.strip().split('\t'))
            line = fin.readline()
    return data


def batch_train_data(batch_size):
    """Get training data in poem, batch major format

    Args:
        batch_size:

    Returns:
        kw_mats: [4, batch_size, time_steps]
        kw_lens: [4, batch_size]
        s_mats: [4, batch_size, time_steps]
        s_lens: [4, batch_size]
    """
    if not os.path.exists(train_path):
        _gen_train_data()
    with codecs.open(train_path, 'r', 'utf-8') as fin:
        stop = False
        while not stop:
            batch_s = [[] for _ in range(4)]
            batch_kw = [[] for _ in range(4)]
            # NOTE(sdsuo): Modified batch size to remove empty lines in batches
            for i in range(batch_size * 4):
                line = fin.readline()
                if not line:
                    stop = True
                    break
                else:
                    toks = line.strip().split('\t')
                    # NOTE(sdsuo): Removed start token
                    batch_s[i%4].append([ch2int[ch] for ch in toks[0]])
                    batch_kw[i%4].append([ch2int[ch] for ch in toks[1]])
            if batch_size != len(batch_s[0]):
                print 'Batch incomplete with size {}, expecting size {}, dropping batch.'.format(len(batch_s[0]), batch_size)
                break
            else:
                kw_mats = [fill_np_matrix(batch_kw[i], batch_size, VOCAB_SIZE-1) \
                        for i in range(4)]
                kw_lens = [fill_np_array(map(len, batch_kw[i]), batch_size, 0) \
                        for i in range(4)]
                s_mats = [fill_np_matrix(batch_s[i], batch_size, VOCAB_SIZE-1) \
                        for i in range(4)]
                s_lens = [fill_np_array([len(x) for x in batch_s[i]], batch_size, 0) \
                        for i in range(4)]
                yield kw_mats, kw_lens, s_mats, s_lens


def process_sentence(sentence, rev=False, pad_len=None, pad_token=PAD_TOKEN):
    if rev:
        sentence = sentence[::-1]

    sentence_ints = sentence_to_ints(sentence)

    if pad_len is not None:
        result_len = len(sentence_ints)
        for i in range(pad_len - result_len):
            sentence_ints.append(pad_token)

    return sentence_ints


def prepare_batch_predict_data(keyword, previous=[], prev=True, rev=False, align=False):
    # previous sentences
    previous_sentences_ints = []
    for sentence in previous:
        sentence_ints = process_sentence(sentence, rev=rev, pad_len=7 if align else None)
        previous_sentences_ints += [SEP_TOKEN] + sentence_ints

    # keywords
    keywords_ints = process_sentence(keyword, rev=rev, pad_len=4 if align else None)

    source_ints = keywords_ints + (previous_sentences_ints if prev else [])
    source_len = len(source_ints)

    source = fill_np_matrix([source_ints], 1, PAD_TOKEN)
    source_len = np.array([source_len])

    return source, source_len


def gen_batch_train_data(batch_size, prev=True, rev=False, align=False):
    """
    Get training data in batch major format, with keyword and previous sentences as source,
    aligned and reversed

    Args:
        batch_size:

    Returns:
        source: [batch_size, time_steps]: keywords + SEP + previous sentences
        source_lens: [batch_size]: length of source
        target: [batch_size, time_steps]: current sentence
        target_lens: [batch_size]: length of target
    """
    if not os.path.exists(train_path):
        _gen_train_data()

    with codecs.open(train_path, 'r', 'utf-8') as fin:
        stop = False
        while not stop:
            source = []
            source_lens = []
            target = []
            target_lens = []

            previous_sentences_ints = []
            for i in range(batch_size):
                line = fin.readline()
                if not line:
                    stop = True
                    break
                else:
                    line_number = i % 4
                    if line_number == 0:
                        previous_sentences_ints = []

                    current_sentence, keywords = line.strip().split('\t')

                    current_sentence_ints = process_sentence(current_sentence, rev=rev, pad_len=7 if align else None)
                    keywords_ints = process_sentence(keywords, rev=rev, pad_len=4 if align else None)
                    source_ints = keywords_ints + (previous_sentences_ints if prev else [])

                    target.append(current_sentence_ints)
                    target_lens.append(len(current_sentence_ints))

                    source.append(source_ints)
                    source_lens.append(len(source_ints))

                    # Always append to previous sentences
                    previous_sentences_ints += [SEP_TOKEN] + current_sentence_ints

            if len(source) == batch_size:
                source_padded = fill_np_matrix(source, batch_size, PAD_TOKEN)
                target_padded = fill_np_matrix(target, batch_size, PAD_TOKEN)
                source_lens = np.array(source_lens)
                target_lens = np.array(target_lens)

                yield source_padded, source_lens, target_padded, target_lens


def main():
    train_data = get_train_data()
    print "Size of the training data: %d" %len(train_data)
    kw_train_data = get_kw_train_data()
    print "Size of the keyword training data: %d" %len(kw_train_data)
    assert len(train_data) == 4 * len(kw_train_data)


if __name__ == '__main__':
    main()
