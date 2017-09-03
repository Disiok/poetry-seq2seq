// includes
var db = require('./db');
var express = require('express');
const mustache = require('mustache-express');
const bodyParser = require('body-parser');

// application
var app = express();

app.use("/", express.static('public'));
app.use(bodyParser.urlencoded({extended: true}));

app.engine('mustache', mustache());
app.set('view engine', 'mustache');

// GET endpoints
app.get('/', function (req, res) {
  db.generateTrial().then(function (trial) {
    res.render('turing',
        { "poem1": trial.poem,
        "poem_id": trial.poem_id,
        "trial_id": trial.trial_id,
        "poem1sentiment": trial.poem1sentiment,
        "poem1textcolor": trial.poem1textcolor
        });
  });
});

app.get('/charts', function(req, res) {
  res.render('charts');
});

app.get('/chartInfo', function(req, res){
  var results = db.tallyResults();
  // all added one to avoid render problem in chart
  results.humanClickedHuman += 1;
  results.humanTotal += 2;
  results.rnnClickedHuman += 1;
  results.rnnTotal += 2;
  res.send(results);
});

app.get('/ajaxGetData', function(req, res){
  db.generateTrial().then(function (trial) {
    res.send({ "poem1": trial.poem,
      "poem_id": trial.poem_id,
      "trial_id": trial.trial_id,
      "poem1sentiment": trial.poem1sentiment,
      "poem1textcolor": trial.poem1textcolor
    });
  });
});

// POST endpoints
app.post('/ajaxSendData', function(req, res) {
  guess = req.body;

  console.log('Received survey result: ');
  console.log(guess);

  db.createRecord(req.body);
  db.isGuessCorrect(guess).then(function (isCorrect) {
    res.send({"result": isCorrect});
  })
});


// running application
var port = process.env.PORT || 8080;
app.listen(port, "0.0.0.0", function () {
  console.log("Running on port " + port);
});

// exports
module.exports = app;
