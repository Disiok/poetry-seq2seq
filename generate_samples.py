# encoding=utf8

from utils import DATA_SAMPLES_DIR
from cnt_words import get_pop_quatrains
from plan import Planner
from seq2seq_predict import Seq2SeqPredictor
import random
import os
import string
human_samples_path = os.path.join(DATA_SAMPLES_DIR, 'human.txt')
rnn_samples_path = os.path.join(DATA_SAMPLES_DIR, 'rnn.txt')


def sample_poems(poems, num=4000):
    sampled_poems = random.sample(poems, num)
    return sampled_poems


def generate_human_samples(sampled_poems):
    with open(human_samples_path, 'a') as fout:
        for poem in sampled_poems:
            for idx, sentence in enumerate(poem['sentences']):
                punctuation = u'\uff0c' if idx % 2 == 0 else u'\u3002'
                line = (sentence + punctuation + '\n').encode('utf-8')
                fout.write(line)


def generate_rnn_samples(sampled_poems):
    planner = Planner()
    results = []
    with Seq2SeqPredictor() as predictor:
        for poem in sampled_poems:
            input = string.join(poem['sentences']).strip()
            keywords = planner.plan(input)
            lines = predictor.predict(keywords)
            results += lines
    with open(rnn_samples_path, 'a') as fout:
        for idx, sentence in enumerate(results):
            punctuation = u'\uff0c' if idx % 2 == 0 else u'\u3002'
            line = (sentence + punctuation + '\n').encode('utf-8')
            fout.write(line)


def load_samples(file_path):
    with open(file_path) as fin:
        lines = fin.read().decode('utf-8').split()
        lines_clean = map(lambda line: line[:-1], lines) # remove punctuations
    poems = [lines_clean[i: i + 4] for i in range(0, len(lines_clean), 4)]
    return poems


def load_human_samples():
    return load_samples(human_samples_path)


def load_rnn_samples():
    return load_samples(rnn_samples_path)
            

def main():
    poems = get_pop_quatrains()
    sampled_poems = sample_poems(poems)
    generate_human_samples(sampled_poems)
    generate_rnn_samples(sampled_poems)

if __name__ == '__main__':
    main()
