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
        console.log(res.result? 'Ajax correct': 'Ajax incorrect');
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

    $('#choice1').attr('poem_id', result.poem_id)

  }});
}
