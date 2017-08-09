// Changelog: humanData -> Human
var humanData = [
  {
    label: 'user clicked human',
    value: 5,
    color: '#174D6B'
  },
  {
    label: 'user clicked computer',
    value: 5,
    color: '#91C6B2'
  }
];
// Changelog: rnn -> rnn
var rnnData = [
  {
    label: 'user clicked human',
    value: 5,
    color: '#174D6B'
  },
  {
    label: 'user clicked computer',
    value: 5,
    color: '#91C6B2'
  }
];
var humanChart;
var rnnChart;
$(document).ready(function()
{
  //alert("document ready");
  var humanContext = document.getElementById('human').getContext('2d');
  humanChart = new Chart(humanContext).Pie(humanData);
  var rnnContext = document.getElementById('rnn').getContext('2d');
  rnnChart = new Chart(rnnContext).Pie(rnnData);
  getTotals();

  setInterval(function(){
    getTotals();
  }, 1000);
})
function getTotals() {
  $.ajax({url: "/chartInfo", success: function(result){
    //alert(result.humanRight);
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
