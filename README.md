# Chinese Poetry Generation


## Dependencies
[Python 2.7](https://www.python.org/download/releases/2.7/)
[TensorFlow 1.2.1](https://www.tensorflow.org/)
[Jieba 0.38](https://github.com/fxsjy/jieba)
[Gensim 2.0.0](https://radimrehurek.com/gensim/)
[pypinyin 0.23](https://pypi.python.org/pypi/pypinyin)

## Features
**Network:**
- [x] Bidirectional encoder
- [x] Attention decoder

**Training and Predicting:**
- [x] Alignment boosted word2vec
- [x] Data mode: reversed
- [x] Data mode: aligned
- [x] Training mode: ground truth
- [x] Training mode: scheduled sampling
- [x] Predicting mode: greedy
- [x] Predicting mode: sampling
- [ ] Predicting mode: beam search

**Refinement:**
- [x] Output refiner
- [ ] Reinforcement learning tuner
- [ ] Iterative polishing

**Evaluation:**
- [x] Evaluation: rhyming
- [x] Evaluation: tonal structure
- [ ] Evaluation: alignment score
- [ ] Evaluation: BLEU score


## Project Structure


## Data Processing

To begin with, you should process the raw data to generate the training data:
```sh
python data_utils.py
```

The TextRank algorithm may take many hours to run.
Instead, you could choose to stop it early by typing ctrl+c to interrupt the iterations,
when the progress shown in the terminal has remained stationary for a long time.

Then, generate the word embedding data using gensim Word2Vec model:
```sh
python word2vec.py
```


## Training

To train the default model:
```sh
python train.py
```

## Generating

Start the user interaction program in a terminal once the training has finished:

    python main.py

Type in an input sentence each time and the poem generator will create a poem for you.

