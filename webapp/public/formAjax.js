$(document).ready(function() {
  $("#turing-form").submit(function (event) {
    event.preventDefault();

    $.post(
      "ajaxSendData",
      $("#turing-form").serialize() + '&poem=' + $('#poem-id').text(),
      function(res) {
        console.log(res.result? 'Ajax correct': 'Ajax incorrect');
        updateCounter(res.result);
      }
    );

    updatePoems();
  });

  $("#skip-button").click(function (event) {
    updatePoems();

    event.preventDefault();
  })
});


var correct = 0;
var total = 0;

function updateCounter(isCorrect) {
  if (isCorrect)
    correct++;
  total++;
  var percent = ~~(100 * correct/total);

  $("#score").text(percent + "%" + " (" + correct + "/" + total + ")");

  $('#score-indicator').text(isCorrect? "Correct" : "Incorrect"); 
  $('#score-indicator').removeClass().addClass(isCorrect? 'badge badge-success' : 'badge badge-danger');
}

function updatePoems(){
  $.ajax({url: "/ajaxGetData", success: function(result){
    $('#poem-content').html(result.content);
    $('#poem-id').text(result._id);
  }});
}
