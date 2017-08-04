# encoding=utf8

from utils import DATA_SAMPLES_DIR
from cnt_words import get_pop_quatrains
from plan import Planner
from predict import Seq2SeqPredictor
import random
import os
import string
import os.path


human_samples_path = os.path.join(DATA_SAMPLES_DIR, 'human.txt')
rnn_samples_path = os.path.join(DATA_SAMPLES_DIR, 'default.txt')


def sample_poems(poems, num=4000):
    sampled_poems = random.sample(poems, num)
    return sampled_poems


def generate_human_samples(sampled_poems):
    with open(human_samples_path, 'w+') as fout:
        for poem in sampled_poems:
            for idx, sentence in enumerate(poem):
                punctuation = u'\uff0c' if idx % 2 == 0 else u'\u3002'
                line = (sentence + punctuation + '\n').encode('utf-8')
                fout.write(line)


def generate_rnn_samples(sampled_poems):
    planner = Planner()
    with Seq2SeqPredictor() as predictor:
        with open(rnn_samples_path, 'w+') as fout:
            for poem_idx, poem in enumerate(sampled_poems):
                input = string.join(poem).strip()
                keywords = planner.plan(input)

                print 'Predicting poem {}.'.format(poem_idx)
                lines = predictor.predict(keywords)

                for idx, sentence in enumerate(lines):
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
    if os.path.exists(human_samples_path):
        print 'Poems already sampled, use the same human samples.'
        cleaned_poems = load_human_samples()
    else:
        print 'Poems not yet sampled, use new human samples.'
        poems = get_pop_quatrains()
        sampled_poems = sample_poems(poems)
        cleaned_poems = map(lambda poem: poem['sentences'], sampled_poems)

        print 'Generating human samples.'
        generate_human_samples(cleaned_poems)

    print 'Generating model samples'
    generate_rnn_samples(cleaned_poems)

if __name__ == '__main__':
    main()
