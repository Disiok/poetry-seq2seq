// Global variables
var charts;
var MEDIUMAQUAMARINE = 'rgba(102, 205, 170, 0.5)';
var LIGHTCORAL = 'rgba(240,128,128, 0.5)';


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
        backgroundColor: [LIGHTCORAL, MEDIUMAQUAMARINE]
      }],
      labels: [
        'False guess as human',
        'Correct guess as computer'
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
        label: 'Computer',
        data: [],
        backgroundColor: LIGHTCORAL
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
      var pieChart = charts['Guess'][author];
      var pieData = pieChart.data.datasets[0].data;
      for (var guessedAuthor of ['Computer', 'Human'].entries()) {
        pieData[guessedAuthor[0]] = result[author]['Guess'][guessedAuthor[1]];
      }

      var radarChart = charts['Score'][author];
      var radarData = radarChart.data.datasets[0].data;
      for (var scoreDimension of ['Readability', 'Consistency', 'Poeticness', 'Evocative', 'Overall'].entries()) {
        radarData[scoreDimension[0]] = result[author]['Score'][scoreDimension[1]];
      }

      pieChart.update();
      radarChart.update();
    };


    // $("#humanP").text(100-(~~((result.humanClickedHuman / result.humanTotal)*100)) + "%");
    // $("#rnnP").text(100-(~~((result.rnnClickedHuman / result.rnnTotal)*100)) + "%");
  }});
}
