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

var last_trial_id = 0;
var trials = {};

function getPoem(type) {
  var toR = Q.defer();

  var author = type == "rnn"? "Computer" : "Human";

  Poem
    .find({"author" : author})
    .count().exec(function(err, count){
      var random = Math.floor(Math.random() * count);
      Poem.find({"author":author}).findOne().skip(random).exec(
        function (err, result) {
          // result is random poem
          toR.resolve(result);
        });
  });
  return toR.promise;
}

function generateTrial() {
  var toR = Q.defer();

  // pick if we are using RNN or human
  // fake_id True: rnn, False: human
  // kinda redundant but I am lazy to change it due to legacy code
  var fake_id = flip() == 0;
  var type = fake_id? "rnn": "human";
  var trial_id = last_trial_id++;

  trials[trial_id] = {
    "fake_poem": fake_id,
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

  // return poem.then(function (poem) {
  //   return Q.all([0.35, 0.35])
  //     .then(function (sent) {
  //       return {
  //         "poem": poem,
  //         "trial_id": trial_id,
  //         "poem1sentiment": sentToColor(sent[0]),
  //         "poem1textcolor": textColor(sent[0])
  //       };
  //     });
  // });

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

function flip() {
  return Math.floor((Math.random() * 2));
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


module.exports = {
	trials,
	generateTrial,
	Turing,
	Poem
}