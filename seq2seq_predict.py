#!/usr/bin/env python
# coding: utf-8


import json

import tensorflow as tf

from data_utils import fill_np_array, fill_np_matrix
from seq2seq_model import Seq2SeqModel
from vocab import get_vocab

# Decoding parameters
tf.app.flags.DEFINE_integer('beam_width', 1, 'Beam width used in beamsearch')
tf.app.flags.DEFINE_integer('decode_batch_size', 80, 'Batch size used for decoding')
tf.app.flags.DEFINE_integer('max_decode_step', 500, 'Maximum time step limit to decode')
tf.app.flags.DEFINE_boolean('write_n_best', False, 'Write n-best list (n=beam_width)')
tf.app.flags.DEFINE_string('model_path', None, 'Path to a specific model checkpoint.')
tf.app.flags.DEFINE_string('predict_mode', 'greedy', 'Decode helper to use for predicting')
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
    if FLAGS.model_path is None:
        checkpoint_path = tf.train.latest_checkpoint('model/')
        print 'Model path not specified, using the latest checkpoint at: {}'.format(checkpoint_path)
    else:
        checkpoint_path = FLAGS.model_path
        print 'Model path specified at: {}'.format(checkpoint_path)
    FLAGS.model_path = checkpoint_path

    # Load config saved with model
    config_unicode = json.load(open('%s.json' % FLAGS.model_path, 'rb'))
    config = unicode_to_utf8(config_unicode)

    # Overwrite flags
    for key, value in FLAGS.__flags.items():
        config[key] = value

    return config


def load_model(session, model, saver):
    if tf.train.checkpoint_exists(FLAGS.model_path):
        print 'Reloading model parameters..'
        model.restore(session, saver, FLAGS.model_path)
    else:
        raise ValueError(
            'No such file:[{}]'.format(FLAGS.model_path))
    return model


class Seq2SeqPredictor:
    def __init__(self):
        # Load model config
        config = load_config(FLAGS)

        # Get vocab
        self.int2ch, self.ch2int = get_vocab()

        config_proto = tf.ConfigProto(
            allow_soft_placement=FLAGS.allow_soft_placement,
            log_device_placement=FLAGS.log_device_placement,
            gpu_options=tf.GPUOptions(allow_growth=True)
        )

        self.sess = tf.Session(config=config_proto)

        # Build the model
        self.model = Seq2SeqModel(config, 'predict')

        # Create saver
        # Using var_list = None returns the list of all saveable variables
        saver = tf.train.Saver(var_list=None)

        # Reload existing checkpoint
        load_model(self.sess, self.model, saver)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sess.close()

    def predict(self, keywords, rev=True):
        sentences = []
        previous = []
        for keyword in keywords:
            source = fill_np_matrix([[self.ch2int[ch] for ch in keyword] + previous], 1, 5999)
            source_len = fill_np_array([len(source[0])], 1, 0)

            predicted = self.model.predict(
                self.sess,
                encoder_inputs=source,
                encoder_inputs_length=source_len
            )

            sentences.append(''.join(map(lambda x: self.int2ch[x[0]], predicted[0])[:-1]))
            previous += [0] + map(lambda x: x[0], predicted[0])[:-1]
        return sentences


def main(_):
    KEYWORDS = [
        u'楚',
        u'收拾',
        u'思乡',
        u'相随'
    ]

    with Seq2SeqPredictor() as predictor:
        lines = predictor.predict(KEYWORDS)
        for line in lines:
            print line

if __name__ == '__main__':
    tf.app.run()
