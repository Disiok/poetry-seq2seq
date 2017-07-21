#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os

VOCAB_SIZE = 6000
SEP_TOKEN = 0
PAD_TOKEN = 5999


DATA_RAW_DIR = 'data/raw'
DATA_PROCESSED_DIR = 'data/processed'
DATA_SAMPLES_DIR = 'data/samples'
MODEL_DIR = 'model'
LOG_DIR = 'log'


if not os.path.exists(DATA_PROCESSED_DIR):
    os.mkdir(DATA_PROCESSED_DIR)
if not os.path.exists(MODEL_DIR):
    os.mkdir(MODEL_DIR)


def embed_w2v(embedding, data_set):
    embedded = [map(lambda x: embedding[x], sample) for sample in data_set]
    return embedded


def apply_one_hot(data_set):
    applied = [map(lambda x: to_categorical(x, num_classes=VOCAB_SIZE)[0], sample) for sample in data_set]
    return applied


def apply_sparse(data_set):
    applied = [map(lambda x: [x], sample) for sample in data_set]
    return applied


def pad_to(lst, length, value):
    for i in range(len(lst), length):
        lst.append(value)
    
    return lst


def uprint(x):
    print repr(x).decode('unicode-escape'),


def uprintln(x):
    print repr(x).decode('unicode-escape')


def is_CN_char(ch):
    return ch >= u'\u4e00' and ch <= u'\u9fa5'


def split_sentences(line):
    sentences = []
    i = 0
    for j in range(len(line)+1):
        if j == len(line) or line[j] in [u'，', u'。', u'！', u'？', u'、']:
            if i < j:
                sentence = u''.join(filter(is_CN_char, line[i:j]))
                sentences.append(sentence)
            i = j+1
    return sentences

