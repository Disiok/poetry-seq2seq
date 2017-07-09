#!/usr/bin/env python
# coding: utf-8


import os
import math
import time
import json
import random
from IPython import embed

from collections import OrderedDict

import numpy as np
import tensorflow as tf

from seq2seq_model import Seq2SeqModel
from vocab import get_vocab
from data_utils import fill_np_array, fill_np_matrix

# Decoding parameters
tf.app.flags.DEFINE_integer('beam_width', 1, 'Beam width used in beamsearch')
tf.app.flags.DEFINE_integer('decode_batch_size', 80, 'Batch size used for decoding')
tf.app.flags.DEFINE_integer('max_decode_step', 500, 'Maximum time step limit to decode')
tf.app.flags.DEFINE_boolean('write_n_best', False, 'Write n-best list (n=beam_width)')
tf.app.flags.DEFINE_string('model_path', None, 'Path to a specific model checkpoint.')
tf.app.flags.DEFINE_string('decode_mode', 'sample', 'Decode helper to use for decoding')
tf.app.flags.DEFINE_string('decode_input', 'data/newstest2012.bpe.de', 'Decoding input path')
tf.app.flags.DEFINE_string('decode_output', 'data/newstest2012.bpe.de.trans', 'Decoding output path')

# Runtime parameters
tf.app.flags.DEFINE_boolean('allow_soft_placement', True, 'Allow device soft placement')
tf.app.flags.DEFINE_boolean('log_device_placement', False, 'Log placement of ops on devices')


FLAGS = tf.app.flags.FLAGS

#json loads strings as unicode; we currently still work with Python 2 strings, and need conversion
def unicode_to_utf8(d):
    return dict((key.encode("UTF-8"), value) for (key, value) in d.items())

def load_config(FLAGS):

    # Load config saved with model
    config_unicode = json.load(open('%s.json' % FLAGS.model_path, 'rb'))
    config = unicode_to_utf8(config_unicode)

    # Overwrite flags
    for key, value in FLAGS.__flags.items():
        config[key] = value

    return config

# TODO(sdsuo): Fix this stub
def prepare_batch(vocab):
    int2ch, ch2int = vocab

    keywords = [
        u'楚',
        u'收拾',
        u'思乡',
        u'相随'
    ]
    for keyword in keywords:
        source = fill_np_matrix([[ch2int[ch] for ch in keyword]], 1, 5999)
        source_len = fill_np_array([len(keyword)], 1, 0)

        yield source, source_len

def load_model(session, config):
    model = Seq2SeqModel(config, 'decode')
    if tf.train.checkpoint_exists(FLAGS.model_path):
        print 'Reloading model parameters..'
        model.restore(session, FLAGS.model_path)
    else:
        raise ValueError(
            'No such file:[{}]'.format(FLAGS.model_path))
    return model


def decode():
    # Load model config
    config = load_config(FLAGS)

    # Get vocab
    int2ch, ch2int = get_vocab()

    config_proto = tf.ConfigProto(
        allow_soft_placement=FLAGS.allow_soft_placement,
        log_device_placement=FLAGS.log_device_placement,
        gpu_options=tf.GPUOptions(allow_growth=True)
    )

    with tf.Session(config=config_proto) as sess:
        # Reload existing checkpoint
        model = load_model(sess, config)

        for source, source_len in prepare_batch((int2ch, ch2int)):
            predicted_ids = model.predict(
                sess,
                encoder_inputs=source,
                encoder_inputs_length=source_len
            )

            for id in predicted_ids[0]:
                print int2ch[id[0]],
            print

def main(_):
    decode()


if __name__ == '__main__':
    tf.app.run()