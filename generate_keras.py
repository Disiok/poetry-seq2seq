#! /usr/bin/env python
#-*- coding:utf-8 -*-


# standard
from IPython import embed
import pandas as pd
import numpy as np
import os.path


# frameworks
from keras.models import load_model
from frameworks.seq2seq_keras.models import AttentionSeq2Seq
from gensim.models import Word2Vec


# custom
from vocab import get_vocab
from data_utils import get_train_data
from word2vec import get_word_embedding, _w2v_model_path
from utils import pad_to, embed, save_dir
from data_utils import get_keras_train_data

# logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


# default configs
_BATCH_SIZE = 64
_VOCAB_SIZE = 6000
_WORD_DIM = 128
_MODEL_DEPTH = 4

_INPUT_LENGTH = 25
_OUTPUT_LENGTH = 10

_N_EPOCHS = 6
_LEARN_RATE = 0.002
_DECAY_RATE = 0.97

_model_path = os.path.join(save_dir, 'keras_model.h5')


class Generator:
    def __init__(self):
        _, self.ch2int = get_vocab()
        self.w2v_model = Word2Vec.load(_w2v_model_path)
        self.embedding = get_word_embedding(_WORD_DIM)

        if os.path.exists(_model_path):
            self.model = load_model(_model_path)
        else:
            self.model = AttentionSeq2Seq(input_length=_INPUT_LENGTH, 
                                          input_dim=_WORD_DIM, 
                                          hidden_dim=_WORD_DIM, 
                                          output_length=_OUTPUT_LENGTH, 
                                          output_dim=_WORD_DIM, 
                                          depth=_MODEL_DEPTH)
            self.model.compile(loss='mse', optimizer='rmsprop')
   
    def train(self, 
              n_epochs = _N_EPOCHS, 
              learn_rate = _LEARN_RATE, 
              decay_rate = _DECAY_RATE):

        # prepare data
        X_train, Y_train = get_keras_train_data()
        X_train_embedded = embed(self.embedding, X_train)
        Y_train_embedded = embed(self.embedding, Y_train)

        # train
        self.model.fit(X_train_embedded, Y_train_embedded, epochs=_N_EPOCHS, verbose=1)

        self.model.save(_model_path)

    def generate(self, keywords):
        previous_sentences = ''
        outputs = []
        for index, keyword in enumerate(keywords):
            # prepare input
            input_ch = previous_sentences + keyword
            input_int = [self.ch2int[ch] for ch in input_ch]
            input_int_pad = pad_to(input_int, _INPUT_LENGTH, _VOCAB_SIZE - 1)
            input_embedded = [map(lambda x: self.embedding[x], input_int_pad)]
            input_embedded_array = np.array(input_embedded)

            # predict
            output_embedded = self.model.predict(input_embedded_array)

            # prepare output
            output_list = map(lambda word_vec: self.w2v_model.most_similar(positive=word_vec, topn=1), 
                            output_embedded[0])
            output_ch = ''.join(output_ch)

            previous_sentences += output_ch
            outputs.append(output_ch)

            return outputs

if __name__ == '__main__':
    generator = Generator()
    kw_train_data = get_kw_train_data()
    for row in kw_train_data[100:]:
        uprintln(row)
        generator.generate(row)
        print

