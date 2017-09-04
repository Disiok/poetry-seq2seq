// includes
var Q = require("q");
var P = require('./models/poem');
var T = require('./models/turing');

// database connection
var mongoose = require('mongoose');
var dbName = 'poetrygen';
var connectionString = 'mongodb://localhost/' + dbName;
mongoose.connect(connectionString);

// models
var Poem = mongoose.model('Poem', mongoose.model('Poem').schema);
var Turing = mongoose.model('Turing', mongoose.model('Turing').schema);

Poem.find({}).exec(function(error, collection) {
  if (collection.length === 0 ) {
    Poem.create({content: "test", author: "Human"}, console.log);
  }
});

// global variable
var last_trial_id = 0;
var trials = {};

function getPoem(type) {
  var toR = Q.defer();

  Poem
    .find({"author": type})
    .count().exec(function(err, count){
      var random = Math.floor(Math.random() * count);
      Poem.find({"author": type}).findOne().skip(random).exec(
        function (err, poem) {
          var tokens = poem.content.match(/[^，。]+[，。]/g);
          console.log(tokens);

          if (tokens) {
            var lines = tokens.join('<br />')
            poem.content = lines;
          } else {
            console.log('Invalid line tokens.')
          }

          toR.resolve(poem);
        });
  });
  return toR.promise;
}

function generateTrial() {

  var types = ['Human', 'Computer']
  var type = randomChoice(types)

  var trial_id = last_trial_id++;

  trials[trial_id] = {
    "type": type,
		"user_responded": false
  };

  return getPoem(type).then(function (poem) {
    return {
      "poem_id": poem._id,
      "poem": poem.content,
      "trial_id": trial_id,
    };
  });
}

function randomChoice(choices) {
  index = Math.floor(choices.length * Math.random())
  return choices[index];
}

function tallyResults() {
  // var rnnTotal = 0;
  // var humanTotal = 0;
  // var rnnRight = 0;
  // var humanRight = 0;
  // var rnnClickedHuman = 0;
  // var humanClickedHuman = 0;

  // for (var key in trials) {
  //   var trial = trials[key];
  //   if (!trial.user_responded)
  //     continue;

  //   // fake_poem == true if it is from human
  //   if (trial.type == "rnn") {
  //     rnnTotal++;
		// 	if (trial.clicked_human) {
		// 		rnnClickedHuman++;
		// 	}
  //   } else if (trial.type == "human") {
  //     humanTotal++;
  //     if (trial.clicked_human) {
  //       humanClickedHuman++;
  //     }
  //   }
  // }

  // return {"rnnTotal": rnnTotal,
  //   "humanTotal": humanTotal,
  //   "rnnClickedHuman": rnnClickedHuman,
  //   "humanClickedHuman": humanClickedHuman};

  var toR = Q.defer();

  data = {
    'human': {
      'human guessed': null, 
      'computer guessed': null,
    },
    'computer': {
      'human guessed': null,
      'computer guessed': null,
    }
  } 

  Turing.find({}).exec(function(error, collection) {
    for (var turing of collection) {
       Poem.findById(turing.poem).exec().then(function (poem) {
          console.log(poem);
       });
      console.log(turing.poem);
      console.log(turing.author)
    }
  });

  return toR.promise;
}

function createRecord(guess) {
  Turing.create(guess, function(error, obj) {
    if (error) {
      console.log('Failed to record user guess. Error: ');
      console.log(error);
    } else {
      console.log('User guess successfully recorded!')
    }
  });
}

function isGuessCorrect(guess) {
  return Poem.findById(guess.poem).exec().then(function(error, poem) {
    if (error) {
      console.log('Cannot find poem with id: ' + guess.poem);

      return false;
    } else {
      isCorrect = (poem.author == guess.author);
      console.log('User guess is ' + (isCorrect? 'correct' : 'incorrect') + '.');
      console.log('The poem is writte by ' + poem.author + ' but user guessed ' + guess.author + '.');
      
      return isCorrect;
    }
  });
}

// exports
module.exports = {
	trials,
	generateTrial,
	tallyResults,
  createRecord,
  isGuessCorrect
}