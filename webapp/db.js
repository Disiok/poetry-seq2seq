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

  var poem = getPoem(type);

  return poem.then(function (poem) {
    return {
      "poem_id": poem._id,
      "poem": poem.content,
      "trial_id": trial_id,
      "poem1sentiment": sentToColor(0.5),
      "poem1textcolor": textColor(0.5)
    };
  });
}

function sentToColor(num) {
  if (num < .25) {
    return ("#2E3E56");
  } else if (num > .25 && num < .45) {
    return ("#174D6B");
  } else if (num > .45 && num < .55) {
    return ("#4E8981");
  } else if (num > .55 && num < .75) {
    return ("#91C6B2");
  } else if (num > .75) {
    return ("#FCEDC9");
  } else {
    return ("#FCEDC9");
  }
}

function textColor(num) {
  if (num < .25) {
    return ("#F2F1EF");
  } else if (num > .25 && num < .45) {
    return ("#F2F1EF");
  } else if (num > .45 && num < .55) {
    return ("#F2F1EF");
  } else if (num > .55 && num < .75) {
    return ("#2E3E56");
  } else if (num > .75) {
    return ("#2E3E56");
  } else {
    return ("#2E3E56");
  }
}

function randomChoice(choices) {
  index = Math.floor(choices.length * Math.random())
  return choices[index];
}

function tallyResults() {
  var rnnTotal = 0;
  var humanTotal = 0;
  var rnnRight = 0;
  var humanRight = 0;
  var rnnClickedHuman = 0;
  var humanClickedHuman = 0;

  for (var key in trials) {
    var trial = trials[key];
    if (!trial.user_responded)
      continue;

    // fake_poem == true if it is from human
    if (trial.type == "rnn") {
      rnnTotal++;
			if (trial.clicked_human) {
				rnnClickedHuman++;
			}
    } else if (trial.type == "human") {
      humanTotal++;
      if (trial.clicked_human) {
        humanClickedHuman++;
      }
    }
  }

  return {"rnnTotal": rnnTotal,
    "humanTotal": humanTotal,
    "rnnClickedHuman": rnnClickedHuman,
    "humanClickedHuman": humanClickedHuman};
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
  var toR = Q.defer();

  Poem.findById(guess.poem).exec(function(error, poem) {
    if (error) {
      console.log('Cannot find poem with id: ' + guess.poem);

      toR.resolve(false);
    } else {
      isCorrect = (poem.author == guess.author);
      console.log('User guess is ' + (isCorrect? 'correct' : 'incorrect') + '.');
      console.log('The poem is writte by ' + poem.author + ' but user guessed ' + guess.author + '.');
      
      toR.resolve(isCorrect);
    }
  });

  return toR.promise;
}

// exports
module.exports = {
	trials,
	generateTrial,
	tallyResults,
  createRecord,
  isGuessCorrect
}