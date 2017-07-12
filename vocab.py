#! /usr/bin/env python
#-*- coding:utf-8 -*-

import os
import codecs
import json

from utils import VOCAB_SIZE, DATA_PROCESSED_DIR, uprint
from corpus import get_all_corpus


_vocab_path = os.path.join(DATA_PROCESSED_DIR, 'vocab.json')


def _gen_vocab():
    print "Generating the vocabulary ..."
    corpus = get_all_corpus()
    char_cnts = dict()
    for idx, poem in enumerate(corpus):
        for sentence in poem['sentences']:
            for ch in sentence:
                char_cnts[ch] = char_cnts[ch]+1 if ch in char_cnts else 1
        if 0 == (idx+1)%10000:
            print "[Vocabulary] %d/%d poems have been processed." %(idx+1, len(corpus))
    vocab = sorted([ch for ch in char_cnts], key = lambda ch: -char_cnts[ch])[:VOCAB_SIZE-2]
    with codecs.open(_vocab_path, 'w', 'utf-8') as fout:
        json.dump(vocab, fout)
    print "The vocabulary has been built."


def get_vocab():
    if not os.path.exists(_vocab_path):
        _gen_vocab()
    int2ch = [u'<START>']
    with codecs.open(_vocab_path, 'r', 'utf-8') as fin:
        int2ch.extend(json.load(fin))
    int2ch.append(u'<PAD>')
    ch2int = dict((ch, idx) for idx, ch in enumerate(int2ch))
    return int2ch, ch2int


int2ch, ch2int = get_vocab()


def int_to_ch(i):
    return int2ch[i]


def ch_to_int(ch):
    return ch2int[ch]


def sentence_to_ints(sentence):
    return map(ch_to_int, sentence)


def ints_to_sentence(ints):
    return ''.join(map(int_to_ch, ints))


def main():
    int2ch, _ = get_vocab()
    print "Size of the vocabulary: {}".format(len(int2ch))
    for ch in int2ch[:100]:
        uprint(ch)


if __name__ == '__main__':
    main()