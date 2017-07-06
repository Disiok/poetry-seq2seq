#! /usr/bin/env python
# -*- coding:utf-8 -*-

import codecs
import sys
import os
import json
import random
import numpy as np
from keras.utils.np_utils import to_categorical

VOCAB_SIZE = 6000

raw_dir = 'raw'
data_dir = 'data'
save_dir = 'save'
log_dir = 'log'

if not os.path.exists(data_dir):
    os.mkdir(data_dir)
if not os.path.exists(save_dir):
    os.mkdir(save_dir)

def embed_w2v(embedding, data_set):
    embedded = [map(lambda x: embedding[x], sample) for sample in data_set]
    return embedded

def apply_one_hot(data_set):
    applied = [map(lambda x: to_categorical(x, num_classes=VOCAB_SIZE), sample) for sample in data_set]
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

