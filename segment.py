#! /usr/bin/env python
#-*- coding:utf-8 -*-

import os
import codecs
import jieba

from utils import DATA_RAW_DIR, DATA_PROCESSED_DIR


sxhy_raw = os.path.join(DATA_RAW_DIR, 'shixuehanying.txt')
sxhy_path = os.path.join(DATA_PROCESSED_DIR, 'sxhy_dict.txt')


def _gen_sxhy_dict():
    sxhy_dict = dict()
    with codecs.open(sxhy_raw, 'r', 'utf-8') as fin:
        line = fin.readline().strip()
        while line:
            if line.startswith('<begin>'):
                tag = line.split('\t')[2]
            elif not line.startswith('<end>'):
                toks = line.split('\t')
                if len(toks) == 3:
                    toks = toks[2].split(' ')
                    tok_list = []
                    for tok in toks:
                        if len(tok) < 4:
                            tok_list.append(tok)
                        else:
                            tok_list.extend(jieba.lcut(tok, HMM=True, cut_all=True))
                    for tok in tok_list:
                        sxhy_dict[tok] = tag
            line = fin.readline().strip()
    with codecs.open(sxhy_path, 'w', 'utf-8') as fout:
        for word in sxhy_dict:
            fout.write(word+'\n')


def get_sxhy_dict():
    sxhy_dict = set()
    with codecs.open(sxhy_path, 'r', 'utf-8') as fin:
        line = fin.readline()
        while line:
            sxhy_dict.add(line.strip())
            line = fin.readline()
    return sxhy_dict


class Segmenter:

    def __init__(self):
        if not os.path.exists(sxhy_path):
            _gen_sxhy_dict()

        print 'Loading sxhy dictionary into jieba.'
        jieba.load_userdict(sxhy_path)

        self._sxhy_dict = get_sxhy_dict()

    def segment(self, sentence):
        if 0 == len(sentence):
            return []
        elif 1 == len(sentence):
            return [sentence]
        elif 2 == len(sentence):
            return [sentence] if sentence in self._sxhy_dict else jieba.lcut(sentence, HMM=True, cut_all=True)
        else:
            segs = []
            for i in range(0, len(sentence), 2):
                if i+3 == len(sentence):
                    if sentence[i:] in self._sxhy_dict:
                        segs.append(sentence[i:])
                    elif sentence[i:i+2] in self._sxhy_dict and sentence[i+1:] not in self._sxhy_dict:
                        segs.extend([sentence[i:i+2], sentence[i+2:]])
                    elif sentence[i:i+2] not in self._sxhy_dict and sentence[i+1:] in self._sxhy_dict:
                        segs.extend([sentence[i:i+1], sentence[i+1:]])
                    else:
                        segs.extend(jieba.lcut(sentence[i:], HMM=True, cut_all=True))
                    break
                elif sentence[i:i+2] in self._sxhy_dict:
                    segs.append(sentence[i:i+2])
                else:
                    segs.extend(jieba.lcut(sentence[i:i+2], HMM=True, cut_all=True))
            return filter(lambda seg: len(seg) > 0, segs)

