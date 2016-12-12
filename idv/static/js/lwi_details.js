$(function(){
  $('.reject').click(function() {
    $.ajax({
      url: window.location,
      type: 'DELETE',
      headers: {'X-CSRFToken': $.cookie('csrftoken')},
      success: function() {
            window.location.pathname = window.DjangoUrls.lwi_requests;
        }
    })
  });
})
