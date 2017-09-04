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
      {
        "poem": trial.content,
        "poem_id": trial._id
      }
    );
  });
});

app.get('/charts', function(req, res) {
  res.render('charts');
});

app.get('/chartInfo', function(req, res){
  db.tallyResults().then(function (result) {
    res.send(result);
  });
});

app.get('/ajaxGetData', function(req, res){
  db.generateTrial().then(function (trial) {
    res.send(trial);
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
