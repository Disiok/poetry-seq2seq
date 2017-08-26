## What it does

A Turing Test for [Chinese Poetry Generation](https://cs.uwaterloo.ca/~mli/Simon_Vera.pdf)

## How we built it

The poetry is generated randomly in two ways:

1.  4000 poems were randomly sampled from 70000+ poems written by human
2.  4000 poems were generated using bidirectional RNN with attention mechanism

The website was built on NodeJs and the color scheme changes depending on the mood of the poems using Indico.

## Demo:

- [Chinese Poetry Generation](http://ming-gpu-3.cs.uwaterloo.ca:8080)
- [Stats](http://ming-gpu-3.cs.uwaterloo.ca:8080/charts)

## Dependency:

- Node.js
- npm
- MongoDB


## How to run it:
````npm install```
````npm start```

## How to import a sample poem database
```mongoimport --db poetrygen --collection poems --drop --file PATH-TO-GIT-REPO/Poem-db-init.json```

# Acknowledgement
Thanks to Ryan Marcus for [the great project](https://github.com/RyanMarcus/EdgarAllanPoetry)
Our implementation of RNN was mainly based on [this paper](https://arxiv.org/abs/1610.09889)