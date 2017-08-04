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
- [x] Data mode: only keywords (no preceding sentences)
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
To prepare training data:
```sh
python data_utils.py
```

> **Note**
> The TextRank algorithm may take many hours to run.
> Instead, you can choose to interrupt the iterations and stop it early,
> when the progress shown in the terminal has remained stationary for a long time.
  
Then, to generate the word embedding:
```sh
python word2vec.py
```

> **Alternative**
> As an alternative, we have also provided pre-processed data in the `data/starterkit` directory
> You may simply perform `cp data/starterkit/* data/processed` to skip the data processing step

## Training

To train the default model:
```sh
python train.py
```

To view the full list of configurable training parameters:
```sh
python train.py -h
```


## Generating

To start the user interation program:
```sh
python main.py
```

## Evaluating

