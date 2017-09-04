// Global variables
var humanChart;
var computerChart;

$(document).ready(function() {
  // Get context
  var humanContext = $('#human-chart');
  var computerContext = $('#computer-chart');

  var humanRadarContext = $('#human-radar');
  var computerRadarContext = $('#computer-radar');

  // Initialize charts
  humanChart = new Chart(humanContext, {
    type: 'pie',
    data: {
      datasets: [{
        data: [],
        backgroundColor: ['MEDIUMAQUAMARINE', 'LIGHTCORAL']
      }],
      labels: [
        'Correct guess as human',
        'False guess as computer'
      ],
    }
  });

  computerChart = new Chart(computerContext, {
    type: 'pie',
    data: {
      datasets: [{
        data: [],
        backgroundColor: ['LIGHTCORAL', 'MEDIUMAQUAMARINE']
      }],
      labels: [
        'False guess as human',
        'Correct guess as computer'
      ]
    }
  });

  humanRadar = new Chart(humanRadarContext, {
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
        data: []
      }]
    }
  });

  computerRadar = new Chart(computerRadarContext, {
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
        data: []
      }]
    }
  });

  // Update charts
  getTotals();
  setInterval(getTotals, 1000);
});

function getTotals() {
  $.ajax({url: "/chartInfo", success: function(result){
    humanChart.data.datasets[0].data[0] = result['Human']['Human'];
    humanChart.data.datasets[0].data[1] = result['Human']['Computer'];

    computerChart.data.datasets[0].data[0] = result['Computer']['Human'];
    computerChart.data.datasets[0].data[1] = result['Computer']['Computer'];
    
    humanChart.update();
    computerChart.update();

    $("#humanP").text(100-(~~((result.humanClickedHuman / result.humanTotal)*100)) + "%");

    $("#rnnP").text(100-(~~((result.rnnClickedHuman / result.rnnTotal)*100)) + "%");
  }});
}
