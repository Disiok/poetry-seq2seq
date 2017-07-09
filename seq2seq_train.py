#!/usr/bin/env python
# coding: utf-8

import time
import os
import math
import json
from collections import OrderedDict
from IPython import embed


import tensorflow as tf

from seq2seq_model import Seq2SeqModel
from data_utils import batch_train_data
from word2vec import get_word_embedding

# Data loading parameters
tf.app.flags.DEFINE_string('source_vocabulary', 'data/europarl-v7.1.4M.de.json', 'Path to source vocabulary')
tf.app.flags.DEFINE_string('target_vocabulary', 'data/europarl-v7.1.4M.fr.json', 'Path to target vocabulary')
tf.app.flags.DEFINE_string('source_train_data', 'data/europarl-v7.1.4M.de', 'Path to source training data')
tf.app.flags.DEFINE_string('target_train_data', 'data/europarl-v7.1.4M.fr', 'Path to target training data')
tf.app.flags.DEFINE_string('source_valid_data', 'data/newstest2012.bpe.de', 'Path to source validation data')
tf.app.flags.DEFINE_string('target_valid_data', 'data/newstest2012.bpe.fr', 'Path to target validation data')

# Network parameters
tf.app.flags.DEFINE_string('cell_type', 'lstm', 'RNN cell for encoder and decoder, default: lstm')
tf.app.flags.DEFINE_string('attention_type', 'bahdanau', 'Attention mechanism: (bahdanau, luong), default: bahdanau')
tf.app.flags.DEFINE_integer('hidden_units', 128, 'Number of hidden units in each layer')
tf.app.flags.DEFINE_integer('depth', 4, 'Number of layers in each encoder and decoder')
tf.app.flags.DEFINE_integer('embedding_size', 128, 'Embedding dimensions of encoder and decoder inputs')
tf.app.flags.DEFINE_integer('num_encoder_symbols', 30000, 'Source vocabulary size')
tf.app.flags.DEFINE_integer('num_decoder_symbols', 30000, 'Target vocabulary size')
# NOTE(sdsuo): We used the same vocab for source and target
tf.app.flags.DEFINE_integer('vocab_size', 6000, 'General vocabulary size')

tf.app.flags.DEFINE_boolean('use_residual', True, 'Use residual connection between layers')
tf.app.flags.DEFINE_boolean('attn_input_feeding', False, 'Use input feeding method in attentional decoder')
tf.app.flags.DEFINE_boolean('use_dropout', True, 'Use dropout in each rnn cell')
tf.app.flags.DEFINE_float('dropout_rate', 0.3, 'Dropout probability for input/output/state units (0.0: no dropout)')

# Training parameters
tf.app.flags.DEFINE_float('learning_rate', 0.0002, 'Learning rate')
tf.app.flags.DEFINE_float('max_gradient_norm', 1.0, 'Clip gradients to this norm')
tf.app.flags.DEFINE_integer('batch_size', 64, 'Batch size')
tf.app.flags.DEFINE_integer('max_epochs', 10, 'Maximum # of training epochs')
tf.app.flags.DEFINE_integer('max_load_batches', 20, 'Maximum # of batches to load at one time')
tf.app.flags.DEFINE_integer('max_seq_length', 50, 'Maximum sequence length')
tf.app.flags.DEFINE_integer('display_freq', 100, 'Display training status every this iteration')
tf.app.flags.DEFINE_integer('save_freq', 100, 'Save model checkpoint every this iteration')
tf.app.flags.DEFINE_integer('valid_freq', 1150000, 'Evaluate model every this iteration: valid_data needed')
tf.app.flags.DEFINE_string('optimizer', 'adam', 'Optimizer for training: (adadelta, adam, rmsprop)')
tf.app.flags.DEFINE_string('model_dir', 'model/', 'Path to save model checkpoints')
tf.app.flags.DEFINE_string('summary_dir', 'model/summary', 'Path to save model summary')
tf.app.flags.DEFINE_string('model_name', 'translate.ckpt', 'File name used for model checkpoints')
tf.app.flags.DEFINE_boolean('shuffle_each_epoch', True, 'Shuffle training dataset for each epoch')
tf.app.flags.DEFINE_boolean('sort_by_length', True, 'Sort pre-fetched minibatches by their target sequence lengths')
tf.app.flags.DEFINE_boolean('use_fp16', False, 'Use half precision float16 instead of float32 as dtype')

# TODO(sdsuo): Make start token and end token more robust
tf.app.flags.DEFINE_integer('start_token', 0, 'Start token')
tf.app.flags.DEFINE_integer('end_token', 5999, 'End token')

# Runtime parameters
tf.app.flags.DEFINE_boolean('allow_soft_placement', True, 'Allow device soft placement')
tf.app.flags.DEFINE_boolean('log_device_placement', False, 'Log placement of ops on devices')

FLAGS = tf.app.flags.FLAGS

def load_or_create_model(sess, FLAGS):
    config = OrderedDict(sorted(FLAGS.__flags.items()))
    model = Seq2SeqModel(config, 'train')

    ckpt = tf.train.get_checkpoint_state(FLAGS.model_dir)
    if ckpt and tf.train.checkpoint_exists(ckpt.model_checkpoint_path):
        print 'Reloading model parameters...'
        model.restore(sess, ckpt.model_checkpoint_path)
    else:
        if not os.path.exists(FLAGS.model_dir):
            os.makedirs(FLAGS.model_dir)
        print 'Created new model parameters...'
        sess.run(tf.global_variables_initializer())

    return model

def train():
    config_proto = tf.ConfigProto(
        allow_soft_placement=FLAGS.allow_soft_placement,
        log_device_placement=FLAGS.log_device_placement,
        gpu_options=tf.GPUOptions(allow_growth=True)
    )

    with tf.Session(config=config_proto) as sess:
        # Create a log writer object
        log_writer = tf.summary.FileWriter(FLAGS.model_dir, graph=sess.graph)

        # Create a new model or reload existing checkpoint
        model = load_or_create_model(sess, FLAGS)

        # Load word2vec embedding
        embedding = get_word_embedding(FLAGS.hidden_units)
        model.init_vars(sess, embedding=embedding)

        step_time, loss = 0.0, 0.0
        sents_seen = 0

        start_time = time.time()

        print 'Training...'
        for epoch_idx in xrange(FLAGS.max_epochs):
            if model.global_epoch_step.eval() >= FLAGS.max_epochs:
                print 'Training is already complete.', \
                      'Current epoch: {}, Max epoch: {}'.format(model.global_epoch_step.eval(), FLAGS.max_epochs)
                break


            # Prepare batch training data
            # TODO(sdsuo): Make corresponding changes in data_utils
            for kw_mats, kw_lens, s_mats, s_lens in batch_train_data(FLAGS.batch_size):
                for idx in range(4):
                    source, source_len, target, target_len = kw_mats[idx], kw_lens[idx], s_mats[idx], s_lens[idx]

                    step_loss, summary = model.train(
                        sess,
                        encoder_inputs=source,
                        encoder_inputs_length=source_len,
                        decoder_inputs=target,
                        decoder_inputs_length=target_len
                    )

                    loss += float(step_loss) / FLAGS.display_freq
                    sents_seen += float(source.shape[0]) # batch_size

                    # Display information
                    if model.global_step.eval() % FLAGS.display_freq == 0:

                        avg_perplexity = math.exp(float(loss)) if loss < 300 else float("inf")

                        time_elapsed = time.time() - start_time
                        step_time = time_elapsed / FLAGS.display_freq

                        sents_per_sec = sents_seen / time_elapsed

                        print 'Epoch ', model.global_epoch_step.eval(), 'Step ', model.global_step.eval(), \
                              'Perplexity {0:.2f}'.format(avg_perplexity), 'Step-time ', step_time, \
                              '{0:.2f} sents/s'.format(sents_per_sec)

                        loss = 0
                        sents_seen = 0
                        start_time = time.time()

                        # Record training summary for the current batch
                        log_writer.add_summary(summary, model.global_step.eval())

                # Save the model checkpoint
                if model.global_step.eval() % FLAGS.save_freq == 0:
                    print 'Saving the model..'
                    checkpoint_path = os.path.join(FLAGS.model_dir, FLAGS.model_name)
                    model.save(sess, checkpoint_path, global_step=model.global_step)
                    json.dump(model.config,
                              open('%s-%d.json' % (checkpoint_path, model.global_step.eval()), 'wb'),
                              indent=2)

            # Increase the epoch index of the model
            model.increment_global_epoch_step_op.eval()
            print 'Epoch {0:} DONE'.format(model.global_epoch_step.eval())


        print 'Saving the last model'
        checkpoint_path = os.path.join(FLAGS.model_dir, FLAGS.model_name)
        model.save(sess, checkpoint_path, global_step=model.global_step)
        json.dump(model.config,
                  open('%s-%d.json' % (checkpoint_path, model.global_step.eval()), 'wb'),
                  indent=2)

    print 'Training terminated'



def main(_):
    train()


if __name__ == '__main__':
    tf.app.run()
