$(document).ready(function () {
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  // Delete request sent to delete all data
  $('#deleteAll').click(function(){
    csrf = getCookie("csrftoken");
    $.ajax({
        type : "DELETE",
        url : "/maps/main",
        beforeSend: function(xhr) {
          xhr.setRequestHeader("X-CSRFToken", csrf);
        },
        success: function(result) {
          location.reload();
        },
        error: function(xhr, status, error) {
          alert(error);
      }
    });
  });
});
