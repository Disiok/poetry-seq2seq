// Global variables
var charts;
var MEDIUMAQUAMARINE = 'rgba(102, 205, 170, 0.5)'
var LIGHTCORAL = 'rgba(240,128,128, 0.5)'
var LIGHTBROWN = 'rgba(206, 181, 167, 0.5)'

var models_by_author = {
  'Computer': ['vrae', 'seq2seq'],
  'Human': ['human']
}


$(document).ready(function() {
  // Get context
  var humanContext = $('#human-chart');
  var computerContext = $('#computer-chart');

  var humanRadarContext = $('#human-radar');
  var computerRadarContext = $('#computer-radar');

  // Chart options
  var chartOption = {
    scale: {
      ticks: {
        min: 1,
        max: 5
      }
    }
  }

  // Initialize charts
  var humanChart = new Chart(humanContext, {
    type: 'pie',
    data: {
      datasets: [{
        data: [],
        backgroundColor: [MEDIUMAQUAMARINE, LIGHTCORAL]
      }],
      labels: [
        'Correct guess as human',
        'False guess as computer'
      ],
    },
    options: chartOption
  });

  var computerChart = new Chart(computerContext, {
    type: 'pie',
    data: {
      datasets: [{
        data: [],
        backgroundColor: [LIGHTCORAL, MEDIUMAQUAMARINE, LIGHTCORAL, MEDIUMAQUAMARINE],
      }, {
        data: [],
        backgroundColor: [LIGHTCORAL, MEDIUMAQUAMARINE, LIGHTCORAL, MEDIUMAQUAMARINE],
      }],
      labels: [
        'False guess as human: vrae',
        'Correct guess as computer: vrae',
        'False guess as human: seq2seq',
        'Correct guess as computer: seq2seq'
      ]
    },
    options: chartOption
  });

  var humanRadar = new Chart(humanRadarContext, {
    type: 'radar',
    data: {
      labels: [
        'Readability',
        'Consistency',
        'Poeticness',
        'Evocative',
        'Overall'
      ],
      datasets: [{
        label: 'Human',
        data: [],
        backgroundColor: MEDIUMAQUAMARINE
      }],
    },
    options: chartOption
  });

  var computerRadar = new Chart(computerRadarContext, {
    type: 'radar',
    data: {
      labels: [
        'Readability',
        'Consistency',
        'Poeticness',
        'Evocative',
        'Overall'
      ],
      datasets: [{
        label: 'Computer: vrae',
        data: [],
        backgroundColor: LIGHTCORAL
      }, {
        label: 'Computer: seq2seq',
        data: [],
        backgroundColor: LIGHTBROWN
      }]
    },
    options: chartOption
  });

  charts = {
    'Guess': {
      'Human': humanChart,
      'Computer': computerChart
    },
    'Score': {
      'Human': humanRadar,
      'Computer': computerRadar
    }
  };

  // Update charts
  getTotals();
  setInterval(getTotals, 1000);
});

function getTotals() {
  $.ajax({url: "/chartInfo", success: function(result){
    for (var author of ['Computer', 'Human']) {
      models = models_by_author[author]

      var pieChart = charts['Guess'][author];
      for (var [modeInd, model] of models.entries()) {
        var pieData = pieChart.data.datasets[modeInd].data;
        for (var [guessedAuthorInd, guessedAuthor] of ['Human', 'Computer'].entries()) {
          pieData[guessedAuthorInd + 2 * modeInd] = result[author][model]['Guess'][guessedAuthor];
        }
      }

      var radarChart = charts['Score'][author];
      for (var [modelInd, model] of models.entries()) {
        var radarData = radarChart.data.datasets[modelInd].data;
        for (var [dimInd, scoreDimension] of ['Readability', 'Consistency', 'Poeticness', 'Evocative', 'Overall'].entries()) {
          radarData[dimInd] = result[author][model]['Score'][scoreDimension];
        }
      }

      pieChart.update();
      radarChart.update();
    };


    // $("#humanP").text(100-(~~((result.humanClickedHuman / result.humanTotal)*100)) + "%");
    // $("#rnnP").text(100-(~~((result.rnnClickedHuman / result.rnnTotal)*100)) + "%");
  }});
}
