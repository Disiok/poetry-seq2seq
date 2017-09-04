var humanChart;
var computerChart;

$(document).ready(function() {
  // Get context
  var humanContext = $('#human-chart');
  var computerContext = $('#computer-chart');

  // Initialize charts
  humanChart = new Chart(humanContext, {
    type: 'pie',
    data: null
  });

  computerChart = new Chart(computerContext, {
    type: 'pie',
    data: null
  });

  getTotals();
  // setInterval(getTotals, 1000);
});

function getTotals() {
  $.ajax({url: "/chartInfo", success: function(result){

    if (humanChart.segments[0].value != result.humanClickedHuman || humanChart.segments[1].value != (result.humanTotal - result.humanClickedHuman))
    {
      humanChart.segments[0].value = result.humanClickedHuman;
      humanChart.segments[1].value = result.humanTotal-result.humanClickedHuman;
      humanChart.update();
    }
    if (rnnChart.segments[0].value != result.rnnClickedHuman || rnnChart.segments[1].value != (result.rnnTotal - result.rnnClickedHuman)) {
      rnnChart.segments[0].value = result.rnnClickedHuman;
      rnnChart.segments[1].value = result.rnnTotal-result.rnnClickedHuman;
      rnnChart.update();
    }


    console.log(JSON.stringify(result));
    $("#humanP").text(100-(~~((result.humanClickedHuman / result.humanTotal)*100)) + "%");

    $("#rnnP").text(100-(~~((result.rnnClickedHuman / result.rnnTotal)*100)) + "%");
  }});
}
