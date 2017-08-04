# Chinese Poetry Generation



![Sample generated Chinese poetry](data/resource/generated_poem.png)
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
- [x] Data loading mode: only keywords (no preceding sentences)
- [x] Data loading mode: reversed
- [x] Data loading mode: aligned
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
**Data**  
`data`: directory for `raw` data, `processed` data, pre-processed `starterkit` data, and generated poetry `samples`
`model`: directory for saved neural network models
`log`: directory for training logs
`notebooks`: directory for exploratory/experimental IPython notebooks
`training_scripts`: directory for sample scripts used for training several basic models

**Code**  


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

> **Note**  
> Thus you should almost always train a new model after modifying any of the parameters.  
> Models are by default saved to `model/`. To train a new model, you may either remove the existing model from `model/`  
> or specify a new model path during training with `python train.py --model_dir :new_model:dir:`  


## Generating

To start the user interation program:
```sh
python main.py
```

Similarly, to view the full list of configurable predicting parameters:
```sh
python main.py -h
```

> **Note**  
> The program currently does not check that predication parameters matches corresponding training parameters.  
> User has to ensure, in particular, the data loading mode correspond the one used during traing.  
> (e.g. If training data is `reversed` and `aligned`, then prediction input should also be `reversed` and `aligned`.  
> Otherwise, results may range from subtle differences in output to total crash.  

## Evaluating

