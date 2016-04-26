'use strict';

var Django = window.Django || {};

Django.Data = (function() {
  var my = {};
  var data = null;
  var containerID = 'js-context';

  my.get = function(key) {
    return data[key];
  };

  my.init = function(jsonDataContainerId) {
    var $container = $('#' + containerID);
    var html_data = $container.first().html();
    data = html_data ? JSON.parse(html_data) : {};
  };
  return my;
})();

Django.Csrf = (function() {
  var my = {};

  var getCookie = function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  var csrfSafeMethod = function(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  };

  var setupCSRF = function() {
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
          xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
      }
    });
  };

  my.init = function() {
    setupCSRF();
  };

  return my;
})();
