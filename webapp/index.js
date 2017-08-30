var express = require('express');
var app = express();
var Q = require("q");

// database
var mongoose = require('mongoose');
var dbName = 'poetrygen';
var connectionString = 'mongodb://localhost/' + dbName;
mongoose.connect(connectionString);

// models
var P = require('./models/poem');
var T = require('./models/turing');

var Poem = mongoose.model('Poem', mongoose.model('Poem').schema);
var Turing = mongoose.model('Turing', mongoose.model('Turing').schema);

Poem.find({}).exec(function(error, collection) {
  if (collection.length === 0 ) {
    Poem.create({content: "test", author: "Human"}, console.log);
  }
});


app.use("/", express.static('public'));

const pythonShell = require('python-shell');
const bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({extended: true}));

const mustache = require('mustache-express');
app.engine('mustache', mustache());
app.set('view engine', 'mustache');


var last_trial_id = 0;
var trials = {};

function getPoem(type) {
  var toR = Q.defer();
  // var options = { pythonPath: 'python3'};
  //
  // if (type =="rnn") {
  //   pythonShell.run('pick_selection_rnn.py', options, function (err, poem) {
  //     if (poem == null) {
  //       if (err) console.log(err);
  //       poem = "of his elect content,<br>conform my soul as t were a church<br><br>unto her sacrament<br><br>love<br><br>love is anterior to life,<br><br>posterior to death,<br><br>initial of creation, and<br><br>the exponent of breath<br><br>satisfied<br><br>one blessing had i, than the rest<br><br>so larger to my eyes<br><br>that i stopped gauging, satisfied,<br><br>for this enchanted size<br><br>it was the limit of my dream,<br><br>the focus of my prayer, --<br><br>a perfect, paralyzing bliss<br><br>contented as despair<br><br>i knew no more of want or cold,<br>";
  //       toR.resolve(poem);
  //       return;
  //     }
  //     poem = poem.join("<br />");
  //     toR.resolve(poem);
  //   });
  // } else if (type == "human") {
  //   pythonShell.run('pick_selection_human.py', options, function (err, poem) {
  //     if (poem == null) {
  //       if (err) console.log(err);
  //       poem = "of his elect content,<br>conform my soul as t were a church<br><br>unto her sacrament<br><br>love<br><br>love is anterior to life,<br><br>posterior to death,<br><br>initial of creation, and<br><br>the exponent of breath<br><br>satisfied<br><br>one blessing had i, than the rest<br><br>so larger to my eyes<br><br>that i stopped gauging, satisfied,<br><br>for this enchanted size<br><br>it was the limit of my dream,<br><br>the focus of my prayer, --<br><br>a perfect, paralyzing bliss<br><br>contented as despair<br><br>i knew no more of want or cold,<br>";
  //       toR.resolve(poem);
  //       return;
  //     }
  //     poem = poem.join("<br />");
  //     toR.resolve(poem);
  //   });
  // }
  // return toR.promise;

  var author = type == "rnn"? "Computer" : "Human";

  // @todo: this is not working yet
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

app.get('/charts', function(req, res) {
  res.render('charts');
});

app.get('/chartInfo', function(req, res){
  var results = tallyResults();
  // all added one to avoid render problem in chart
  results.humanClickedHuman += 1;
  results.humanTotal += 2;
  results.rnnClickedHuman += 1;
  results.rnnTotal += 2;
  res.send(results);
});

app.get('/', function (req, res) {
  generateTrial().then(function (trial) {
    res.render('turing',
        { "poem1": trial.poem,
        "poem_id": trial.poem_id,
        "trial_id": trial.trial_id,
        "poem1sentiment": trial.poem1sentiment,
        "poem1textcolor": trial.poem1textcolor
        });
  });
});

app.post('/ajaxSendData', function(req, res) {
  console.log(req.body);

  Turing.create(req.body, function(error, obj) {
    if (error) {
      console.log('Document creation failed.');
      console.log(error);
    } else {
      console.log('Document creation succeeded')
    }
  });

  if (!(req.body.trial_id in trials)) {
    res.send({"result": false});
    return;
  }
  trials[req.body.trial_id].user_responded = req.body.user_responded === "true";
  trials[req.body.trial_id].clicked_human = req.body.clicked_human === "true";

  // return true if correct
  // correct: clicked_human (true if user clicked humanButton) !== fake_poem (not from human)
  res.send({"result": trials[req.body.trial_id].clicked_human !== trials[req.body.trial_id].fake_poem});
});

app.post('/test', function(req, res) {
  console.log(req.body);
  // res.redirect('/');
});


app.get('/ajaxGetData', function(req, res){
  generateTrial().then(function (trial) {
    res.send({ "poem1": trial.poem,
      "poem_id": trial.poem_id,
      "trial_id": trial.trial_id,
      "poem1sentiment": trial.poem1sentiment,
      "poem1textcolor": trial.poem1textcolor
    });
  });
});


var port = process.env.PORT || 8080;
app.listen(port, "0.0.0.0", function () {
  console.log("Running on port " + port);
});

module.exports = app;
