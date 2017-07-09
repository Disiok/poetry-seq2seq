#! /usr/bin/env python
#-*- coding:utf-8 -*-

# standard
import os
from IPython import embed


# framework
import tensorflow as tf
from tensorflow.contrib import rnn, seq2seq

from tensorflow.python.ops.rnn_cell import GRUCell
from tensorflow.python.ops.rnn_cell import LSTMCell
from tensorflow.python.ops.rnn_cell import MultiRNNCell
from tensorflow.python.ops.rnn_cell import DropoutWrapper, ResidualWrapper

from tensorflow.python.ops import array_ops
from tensorflow.python.ops import control_flow_ops
from tensorflow.python.framework import constant_op
from tensorflow.python.framework import dtypes
from tensorflow.python.layers.core import Dense
from tensorflow.python.util import nest

from tensorflow.contrib.seq2seq.python.ops import attention_wrapper
from tensorflow.contrib.seq2seq.python.ops import beam_search_decoder

# custom
from utils import save_dir


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


_model_path = os.path.join(save_dir, 'model')


class Seq2SeqModel:
    """
    Seq2Seq model based on tensorflow.contrib.seq2seq
    """
    def __init__(self, config, mode):

        assert mode.lower() in ['train', 'decode']

        self.config = config
        self.mode = mode.lower()

        self.cell_type = config['cell_type']
        self.hidden_units = config['hidden_units']
        self.depth = config['depth']
        self.attention_type = config['attention_type']
        self.embedding_size = config['embedding_size']
        self.vocab_size = config['vocab_size']
        # self.bidirectional = config.bidirectional

        self.num_encoder_symbols = config['num_encoder_symbols']
        self.num_decoder_symbols = config['num_decoder_symbols']

        self.use_residual = config['use_residual']
        self.attn_input_feeding = config['attn_input_feeding']
        self.use_dropout = config['use_dropout']
        self.keep_prob = 1.0 - config['dropout_rate']

        self.optimizer = config['optimizer']
        self.learning_rate = config['learning_rate']
        self.max_gradient_norm = config['max_gradient_norm']

        self.global_step = tf.Variable(0, trainable=False, name='global_step')
        self.global_epoch_step = tf.Variable(0, trainable=False, name='global_epoch_step')
        self.increment_global_epoch_step_op = tf.assign(self.global_epoch_step, self.global_epoch_step + 1)

        self.dtype = tf.float16 if config['use_fp16'] else tf.float32
        self.keep_prob_placeholder = tf.placeholder(self.dtype, shape=[], name='keep_prob')

        self.use_beamsearch_decode=False
        if self.mode == 'decode':
            self.beam_width = config['beam_width']
            self.use_beamsearch_decode = True if self.beam_width > 1 else False
            self.max_decode_step = config['max_decode_step']

        self.start_token = config['start_token']
        self.end_token = config['end_token']

        self.build_model()

    def build_model(self):
        print 'Building model...'

        # Build encoder and decoder networks
        self.init_placeholders()
        self.build_encoder()
        self.build_decoder()

        # Merge all the training summaries
        self.summary_op = tf.summary.merge_all()

    def init_placeholders(self):
        # TODO(sdsuo): Understand dropout
        self.keep_prob_placeholder = tf.placeholder(self.dtype, shape=[], name='keep_prob')

        # embedding_placeholder: [vocab_size, hidden_units]
        self.embedding_placeholder = tf.placeholder(
            name='embedding_placeholder',
            shape=[self.vocab_size, self.hidden_units],
            dtype=self.dtype
        )

        self.embedding = tf.get_variable(
            name='embedding',
            shape=[self.vocab_size, self.hidden_units],
            trainable=False,
        )

        self.assign_embedding_op = self.embedding.assign(self.embedding_placeholder)

        # encode_inputs: [batch_size, time_steps]
        self.encoder_inputs = tf.placeholder(
            name='encoder_inputs',
            shape=(None, None),
            dtype=tf.int32
        )

        # encoder_inputs_length: [batch_size]
        self.encoder_inputs_length = tf.placeholder(
            name='encoder_inputs_length',
            shape=(None,),
            dtype=tf.int32
        )

        # use dynamic batch_size based on input
        self.batch_size = tf.shape(self.encoder_inputs)[0]

        if self.mode == 'train':
            # decoder_inputs: [batch_size, max_time_steps]
            self.decoder_inputs = tf.placeholder(
                dtype=tf.int32,
                shape=(None, None),
                name='decoder_inputs'
            )

            # decoder_inputs_length: [batch_size]
            self.decoder_inputs_length = tf.placeholder(
                dtype=tf.int32,
                shape=(None,),
                name='decoder_inputs_length'
            )

            # TODO(sdsuo): Make corresponding modification in data_utils
            decoder_start_token = tf.ones(
                shape=[self.batch_size, 1],
                dtype=tf.int32
            ) * self.start_token
            decoder_end_token = tf.ones(
                shape=[self.batch_size, 1],
                dtype=tf.int32
            ) * self.end_token

            # decoder_inputs_train: [batch_size , max_time_steps + 1]
            # insert _GO symbol in front of each decoder input
            self.decoder_inputs_train = tf.concat([decoder_start_token,
                                                  self.decoder_inputs], axis=1)

            # decoder_inputs_length_train: [batch_size]
            self.decoder_inputs_length_train = self.decoder_inputs_length + 1

            # decoder_targets_train: [batch_size, max_time_steps + 1]
            # insert EOS symbol at the end of each decoder input
            self.decoder_targets_train = tf.concat([self.decoder_inputs,
                                                   decoder_end_token], axis=1)

    def build_single_cell(self):
        if self.cell_type == 'gru':
            cell_type = GRUCell
        elif self.cell_type == 'lstm':
            cell_type = LSTMCell
        else:
            raise RuntimeError('Unknown cell type!')
        cell = cell_type(self.hidden_units)

        return cell

    def build_encoder_cell(self):
        multi_cell = MultiRNNCell([self.build_single_cell() for _ in range(self.depth)])

        return multi_cell

    def build_encoder(self):
        print 'Building encoder...'
        with tf.variable_scope('encoder'):
            # Build encoder cell
            self.encoder_cell = self.build_encoder_cell()


            # embedded inputs: [batch_size, time_step, embedding_size]
            self.encoder_inputs_embedded = tf.nn.embedding_lookup(
                params=self.embedding,
                ids=self.encoder_inputs
            )

            # TODO(sdsuo): Decide if we need a Dense input layer here

            # Encode input sequences into context vectors
            # encoder_outputs: [batch_size, time_step, cell_output_size]
            # encoder_last_state: [batch_size, cell_output_size]
            self.encoder_outputs, self.encoder_last_state = tf.nn.dynamic_rnn(
                cell=self.encoder_cell,
                inputs=self.encoder_inputs_embedded,
                sequence_length=self.encoder_inputs_length,
                dtype=self.dtype,
                time_major=False
            )

    def build_decoder_cell(self):
        # TODO(sdsuo): Read up and decide whether to use beam search
        self.attention_mechanism = seq2seq.BahdanauAttention(
            num_units=self.hidden_units,
            memory=self.encoder_outputs,
            memory_sequence_length=self.encoder_inputs_length
        )

        self.decoder_cell_list = [
            self.build_single_cell() for _ in range(self.depth)
        ]

        # NOTE(sdsuo): Not sure what this does yet
        def attn_decoder_input_fn(inputs, attention):
            if not self.attn_input_feeding:
                return inputs

            # Essential when use_residual=True
            _input_layer = Dense(self.hidden_units, dtype=self.dtype,
                                 name='attn_input_feeding')
            return _input_layer(array_ops.concat([inputs, attention], -1))

        # NOTE(sdsuo): Attention mechanism is implemented only on the top decoder layer
        self.decoder_cell_list[-1] = seq2seq.AttentionWrapper(
            cell=self.decoder_cell_list[-1],
            attention_mechanism=self.attention_mechanism,
            attention_layer_size=self.hidden_units,
            cell_input_fn=attn_decoder_input_fn,
            initial_cell_state=self.encoder_last_state[-1],
            alignment_history=False,
            name='attention_wrapper'
        )

        # NOTE(sdsuo): Not sure why this is necessary
        # To be compatible with AttentionWrapper, the encoder last state
        # of the top layer should be converted into the AttentionWrapperState form
        # We can easily do this by calling AttentionWrapper.zero_state

        # Also if beamsearch decoding is used, the batch_size argument in .zero_state
        # should be ${decoder_beam_width} times to the origianl batch_size
        if self.use_beamsearch_decode:
            batch_size = self.batch_size * self.beam_width
        else:
            batch_size = self.batch_size

        initial_state = [state for state in self.encoder_last_state]
        initial_state[-1] = self.decoder_cell_list[-1].zero_state(
            batch_size=batch_size,
            dtype=self.dtype
        )
        decoder_initial_state = tuple(initial_state)


        return MultiRNNCell(self.decoder_cell_list), decoder_initial_state


    def build_decoder(self):
        print 'Building decoder...'
        with tf.variable_scope('decoder'):
            # Building decoder_cell and decoder_initial_state
            self.decoder_cell, self.decoder_initial_state = self.build_decoder_cell()

            # Output projection layer to convert cell_outputs to logits
            output_layer = Dense(self.vocab_size, name='output_projection')

            if self.mode == 'train':
                self.decoder_inputs_embedded = tf.nn.embedding_lookup(
                    params=self.embedding,
                    ids=self.decoder_inputs_train
                )

                training_helper = seq2seq.TrainingHelper(
                    inputs=self.decoder_inputs_embedded,
                    sequence_length=self.decoder_inputs_length_train,
                    time_major=False,
                    name='training_helper'
                )
                training_decoder = seq2seq.BasicDecoder(
                    cell=self.decoder_cell,
                    helper=training_helper,
                    initial_state=self.decoder_initial_state,
                    output_layer=output_layer
                )
                max_decoder_length = tf.reduce_max(self.decoder_inputs_length_train)

                self.decoder_outputs_train, self.decoder_last_state_train, self.decoder_outputs_length_train = seq2seq.dynamic_decode(
                    decoder=training_decoder,
                    output_time_major=False,
                    impute_finished=True,
                    maximum_iterations=max_decoder_length
                )

                # NOTE(sdsuo): Not sure why this is necessary
                self.decoder_logits_train = tf.identity(self.decoder_outputs_train.rnn_output)

                 # Use argmax to extract decoder symbols to emit
                self.decoder_pred_train = tf.argmax(
                    self.decoder_logits_train,
                    axis=-1,
                    name='decoder_pred_train'
                )

                # masks: masking for valid and padded time steps, [batch_size, max_time_step + 1]
                masks = tf.sequence_mask(
                    lengths=self.decoder_inputs_length_train,
                    maxlen=max_decoder_length,
                    dtype=self.dtype,
                    name='masks'
                )

                # Computes per word average cross-entropy over a batch
                # Internally calls 'nn_ops.sparse_softmax_cross_entropy_with_logits' by default
                self.loss = seq2seq.sequence_loss(
                    logits=self.decoder_logits_train,
                    targets=self.decoder_targets_train,
                    weights=masks,
                    average_across_timesteps=True,
                    average_across_batch=True
                )

                # Training summary for the current batch_loss
                tf.summary.scalar('loss', self.loss)

                # Contruct graphs for minimizing loss
                self.init_optimizer()


            elif self.mode == 'decode':
                # start_tokens: [batch_size,]
                start_tokens = tf.ones([self.batch_size,], tf.int32) * self.start_token
                end_token =self.end_token

                if not self.use_beamsearch_decode:

                    # Helper to feed inputs for greedy decoding: use the argmax of the output
                    decoding_helper = seq2seq.GreedyEmbeddingHelper(
                        start_tokens=start_tokens,
                        end_token=end_token,
                        embedding= lambda inputs: tf.nn.embedding_lookup(self.embedding, inputs)
                    )

                    print 'Building greedy decoder...'
                    inference_decoder = seq2seq.BasicDecoder(
                        cell=self.decoder_cell,
                        helper=decoding_helper,
                        initial_state=self.decoder_initial_state,
                        output_layer=output_layer
                    )
                else:
                    raise NotImplementedError


                self.decoder_outputs_decode, self.decoder_last_state_decode,self.decoder_outputs_length_decode = seq2seq.dynamic_decode(
                    decoder=inference_decoder,
                    output_time_major=False,
                    maximum_iterations=self.max_decode_step
                )

                if not self.use_beamsearch_decode:
                    self.decoder_pred_decode = tf.expand_dims(self.decoder_outputs_decode.sample_id, -1)
                else:
                    raise NotImplementedError

            else:
                raise RuntimeError

    def init_optimizer(self):
        print("Setting optimizer..")
        # Gradients and SGD update operation for training the model
        trainable_params = tf.trainable_variables()
        if self.optimizer.lower() == 'adadelta':
            self.opt = tf.train.AdadeltaOptimizer(learning_rate=self.learning_rate)
        elif self.optimizer.lower() == 'adam':
            self.opt = tf.train.AdamOptimizer(learning_rate=self.learning_rate)
        elif self.optimizer.lower() == 'rmsprop':
            self.opt = tf.train.RMSPropOptimizer(learning_rate=self.learning_rate)
        else:
            self.opt = tf.train.GradientDescentOptimizer(learning_rate=self.learning_rate)

        # Compute gradients of loss w.r.t. all trainable variables
        gradients = tf.gradients(self.loss, trainable_params)

        # Clip gradients by a given maximum_gradient_norm
        clip_gradients, _ = tf.clip_by_global_norm(gradients, self.max_gradient_norm)

        # Update the model
        self.updates = self.opt.apply_gradients(
            zip(clip_gradients, trainable_params), global_step=self.global_step)

    def save(self, sess, path, var_list=None, global_step=None):
        """

        Args:
            sess:
            path:
            var_list:
            global_step:

        Returns:

        """
        # Using var_list = None returns the list of all saveable variables
        saver = tf.train.Saver(var_list=var_list)

        save_path = saver.save(sess, save_path=path, global_step=global_step)
        print 'Model saved at {}'.format(save_path)

    def restore(self, sess, path, var_list=None):
        """

        Args:
            sess:
            path:
            var_list:

        Returns:

        """
        # Using var_list = None returns the list of all saveable variables
        saver = tf.train.Saver(var_list=var_list)
        saver.restore(sess, save_path=path)
        print 'Model restored from {}'.format(path)

    def train(self, sess, encoder_inputs, encoder_inputs_length,
              decoder_inputs, decoder_inputs_length):
        """Run a train step of the model feeding the given inputs.

        Args:
          session: tensorflow session to use.
          encoder_inputs: a numpy int matrix of [batch_size, max_source_time_steps]
              to feed as encoder inputs
          encoder_inputs_length: a numpy int vector of [batch_size]
              to feed as sequence lengths for each element in the given batch
          decoder_inputs: a numpy int matrix of [batch_size, max_target_time_steps]
              to feed as decoder inputs
          decoder_inputs_length: a numpy int vector of [batch_size]
              to feed as sequence lengths for each element in the given batch

        Returns:
          A triple consisting of gradient norm (or None if we did not do backward),
          average perplexity, and the outputs.
        """
        # Check if the model is in training mode
        if self.mode != 'train':
            raise ValueError('Train step can only be operated in train mode')

        input_feed = self.check_feeds(encoder_inputs, encoder_inputs_length,
                                      decoder_inputs, decoder_inputs_length, False)

        # TODO(sdsuo): Understand keep prob
        input_feed[self.keep_prob_placeholder.name] = self.keep_prob

        output_feed = [
            self.updates,   # Update Op that does optimization
            self.loss,      # Loss for current batch
            self.summary_op # Training summary
        ]
        outputs = sess.run(output_feed, input_feed)

        return outputs[1], outputs[2]   # loss, summary

    def predict(self, sess, encoder_inputs, encoder_inputs_length):
        input_feed = self.check_feeds(encoder_inputs, encoder_inputs_length,
                                      decoder_inputs=None, decoder_inputs_length=None,
                                      decode=True)

        # Input feeds for dropout
        input_feed[self.keep_prob_placeholder.name] = 1.0

        output_feed = [self.decoder_pred_decode]
        outputs = sess.run(output_feed, input_feed)

        # GreedyDecoder: [batch_size, max_time_step]
        # BeamSearchDecoder: [batch_size, max_time_step, beam_width]
        return outputs[0]

    def init_vars(self, sess, embedding):
        sess.run([self.assign_embedding_op], feed_dict={
            self.embedding_placeholder: embedding
        })

    def check_feeds(self, encoder_inputs, encoder_inputs_length,
                    decoder_inputs, decoder_inputs_length, decode):
        """
        Args:
          encoder_inputs: a numpy int matrix of [batch_size, max_source_time_steps]
              to feed as encoder inputs
          encoder_inputs_length: a numpy int vector of [batch_size]
              to feed as sequence lengths for each element in the given batch
          decoder_inputs: a numpy int matrix of [batch_size, max_target_time_steps]
              to feed as decoder inputs
          decoder_inputs_length: a numpy int vector of [batch_size]
              to feed as sequence lengths for each element in the given batch
          decode: a scalar boolean that indicates decode mode
        Returns:
          A feed for the model that consists of encoder_inputs, encoder_inputs_length,
          decoder_inputs, decoder_inputs_length
        """

        input_batch_size = encoder_inputs.shape[0]
        if input_batch_size != encoder_inputs_length.shape[0]:
            raise ValueError("Encoder inputs and their lengths must be equal in their "
                "batch_size, %d != %d" % (input_batch_size, encoder_inputs_length.shape[0]))

        if not decode:
            target_batch_size = decoder_inputs.shape[0]
            if target_batch_size != input_batch_size:
                raise ValueError("Encoder inputs and Decoder inputs must be equal in their "
                    "batch_size, %d != %d" % (input_batch_size, target_batch_size))
            if target_batch_size != decoder_inputs_length.shape[0]:
                raise ValueError("Decoder targets and their lengths must be equal in their "
                    "batch_size, %d != %d" % (target_batch_size, decoder_inputs_length.shape[0]))

        input_feed = {}

        input_feed[self.encoder_inputs.name] = encoder_inputs
        input_feed[self.encoder_inputs_length.name] = encoder_inputs_length

        if not decode:
            input_feed[self.decoder_inputs.name] = decoder_inputs
            input_feed[self.decoder_inputs_length.name] = decoder_inputs_length

        return input_feed

if __name__ == '__main__':
    model = Seq2SeqModel()
    embed()

