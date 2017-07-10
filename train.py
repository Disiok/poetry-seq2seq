#! /usr/bin/env python
# -*- coding:utf-8 -*-

from utils import *
from data_utils import *
from generate_keras import CategoricalGenerator
from time import sleep


if __name__ == '__main__':
    generator = CategoricalGenerator()
    learn_rate = 0.002
    decay_rate = 0.97
    epoch_no = 0
    epoch_step = 5
    while True:
        generator.train(n_epochs = epoch_step,
                learn_rate = learn_rate*decay_rate**epoch_no,
                decay_rate = decay_rate)
        epoch_no += epoch_step
        print "[Train] %d epochs have finished: 60s cool down ..." %epoch_no
        sleep(60)

