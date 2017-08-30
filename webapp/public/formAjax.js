$(document).ready(function() {
  $("#humanButton").click(function() {
    var trial_id = $("#humanButton").attr("trial_id");
    var poem_id = 0;
    $.post("/ajaxSendData",
      {'trial_id': trial_id,
        'clicked_human': true,
        'user_responded': true},
      function (res) {
        updateCounter(res.result);
      });

    updatePoems();
  });

  $("#computerButton").click(function() {
    var trial_id = $("#computerButton").attr("trial_id");
    var poem_id = 1;
    $.post("/ajaxSendData",
      {'trial_id': trial_id,
        'clicked_human': false,
        'user_responded': true},
      function (res) {
        updateCounter(res.result);
      });

    updatePoems();
  });

  $("#turing-form").submit(function (event) {
    $.post("ajaxSendData",
      $("#turing-form").serialize() + '&poem=' + $('#choice1').attr('poem_id'),
      function(res) {
        updateCounter(res.result);
      });
    updatePoems();

    event.preventDefault();
  });
});


var correct = 0;
var total = 0;
function updateCounter(result) {
  if (result)
    correct++;
  total++;
  var percent = ~~(100 * correct/total);
	// alert(result);
  $("#score").text(percent + "%" + " (" + correct + "/" + total + ")");
}

function updatePoems(){
  $.ajax({url: "/ajaxGetData", success: function(result){
    document.getElementById('choice1').innerHTML = result.poem1;

    $('#choice1').css('background-color', result.poem1color);
    $('#choice2').css('background-color', result.poem2color);
    $('#choice1').css('color', result.poem1textcolor);
    $('#choice2').css('color', result.poem2textcolor);

    $('#humanButton').attr('trial_id', result.trial_id);
    $('#computerButton').attr('trial_id', result.trial_id);
  }});
}
