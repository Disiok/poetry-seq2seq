# -*- coding: utf-8 -*-

import sys
from word2vec import *
from utils import DATA_PROCESSED_DIR
from rhyme import RhymeDict

_w2v_path = os.path.join(DATA_PROCESSED_DIR, 'word2vec.npy')
_w2v_model_path = os.path.join(DATA_PROCESSED_DIR, 'word2vec.model')
_w2v_with_alignment_path = os.path.join(DATA_PROCESSED_DIR, 'word2vec_with_alignment.npy')
_w2v_with_alignment_model_path = os.path.join(DATA_PROCESSED_DIR, 'word2vec_with_alignment.model')

def print_unicode_list(lst):
    msg = repr([x.encode(sys.stdout.encoding) for x in lst]).decode('string-escape')
    print msg

def experiment1():
    model = models.Word2Vec.load(_w2v_model_path)
    model_alignment = models.Word2Vec.load(_w2v_model_path)
    tests = ['一','两','十','七','八','东','南','西','北','红','绿','人','小','玉']
    print "Experiment on similarity between word2vec with alignment or without alignment"
    for test in tests:
        print "==================", test, "=================="
        for m, alignment in zip([model, model_alignment], [False, True]):
            if alignment:
                print "Top similarity from model without alignment:"
            else:
                print "Top similarity from model with alignment:"
            result = [t[0] for t in m.wv.most_similar(positive=[unicode(test, "utf-8")])]
            print_unicode_list(result)

def refine(ch_rhyme, ch, alignment=False, topn=50):
    if alignment:
        model = models.Word2Vec.load(_w2v_model_path)
    else:
        model = models.Word2Vec.load(_w2v_model_path)
    rdict = RhymeDict()
    int2ch, ch2int = get_vocab()
    rhyme = rdict.get_rhyme(unicode(ch_rhyme, "utf-8"))
    result = [t[0] for t in model.wv.most_similar(positive=[unicode(ch, "utf-8")], topn=topn)]
    filtered_result = filter(lambda ch: ch in ch2int, result)
    for target in filtered_result:
        if rdict.get_rhyme(target) == rhyme:
            return target
    return ch

if __name__ == '__main__':
    experiment1()
    from IPython import embed
    embed()