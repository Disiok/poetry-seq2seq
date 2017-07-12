#! /usr/bin/env python
#-*- coding:utf-8 -*-

import os
from utils import DATA_PROCESSED_DIR
import numpy as np
from vocab import get_vocab, VOCAB_SIZE
from quatrains import get_quatrains
from gensim import models
from numpy.random import uniform

_w2v_path = os.path.join(DATA_PROCESSED_DIR, 'word2vec.npy')
_w2v_model_path = os.path.join(DATA_PROCESSED_DIR, 'word2vec.model')
_w2v_with_alignment_path = os.path.join(DATA_PROCESSED_DIR, 'word2vec_with_alignment.npy')
_w2v_with_alignment_model_path = os.path.join(DATA_PROCESSED_DIR, 'word2vec_with_alignment.model')

def _gen_embedding(ndim, alignment=False):
    print "Generating %d-dim word embedding ..." %ndim
    int2ch, ch2int = get_vocab()
    ch_lists = []
    quatrains = get_quatrains()
    for idx, poem in enumerate(quatrains):
        for sentence in poem['sentences']:
            ch_lists.append(filter(lambda ch: ch in ch2int, sentence))
        if alignment:
            # the i-th characters in the poem, used to boost Dui Zhang
            i_characters = [[sentence[j] for sentence in poem['sentences']] for j in range(len(poem['sentences'][0]))]
            for characters in i_characters:
                ch_lists.append(filter(lambda ch: ch in ch2int, characters))
        if 0 == (idx+1)%10000:
            print "[Word2Vec] %d/%d poems have been processed." %(idx+1, len(quatrains))
    print "Hold on. This may take some time ..."
    model = models.Word2Vec(ch_lists, size = ndim, min_count = 5)
    embedding = uniform(-1.0, 1.0, [VOCAB_SIZE, ndim])
    for idx, ch in enumerate(int2ch):
        if ch in model.wv:
            embedding[idx,:] = model.wv[ch]
    if alignment:
        model.save(_w2v_with_alignment_model_path)
        print "Word2Vec model is saved."
        np.save(_w2v_with_alignment_path, embedding)
        print "Word embedding is saved."
    else:
        model.save(_w2v_model_path)
        print "Word2Vec model is saved."
        np.save(_w2v_path, embedding)
        print "Word embedding is saved."

def get_word_embedding(ndim, alignment=False):
    if alignment:
        if not os.path.exists(_w2v_with_alignment_path) or not os.path.exists(_w2v_with_alignment_model_path):
            _gen_embedding(ndim, alignment=True)
        return np.load(_w2v_with_alignment_path)
    else:
        if not os.path.exists(_w2v_path) or not os.path.exists(_w2v_model_path):
            _gen_embedding(ndim)
        return np.load(_w2v_path)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Generate or load a Wrod2Vec embedding')
    parser.add_argument('--alignment', help='Use Wrod2Vec with alignment', action='store_true', required=False)
    args = parser.parse_args()
    if args.alignment:
        print "Using Word2vec with alignment, use -h for usage"
        embedding = get_word_embedding(128, alignment=True)
        print "Finished loading Word2vec with alignment. Size of embedding: (%d, %d)" %embedding.shape
    else:
        print "Using Word2vec without alignment, use -h for usage"
        embedding = get_word_embedding(128)
        print "Finished loading Word2vec without alignment. Size of embedding: (%d, %d)" %embedding.shape


