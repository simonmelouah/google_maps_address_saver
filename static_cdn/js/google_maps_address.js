$(document).ready(function () {
  $('#deleteAll').click(function(){
    $.ajax({
        type : "DELETE",
        url : "/maps/main",
        contentType: 'application/json;charset=UTF-8',
        dataType: "json",
        success: function(result) {
          location.reload();
        }
    });
  });
