function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
$(function(){
  $('.reject').click(function() {
    $.ajax({
      url: window.location,
      type: 'DELETE',
      headers: {'X-CSRFToken': getCookie('csrftoken')},
      success: function() {
            window.location.pathname = window.DjangoUrls.lwi_requests;
        }
    })
  });
})
