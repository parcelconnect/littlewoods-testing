"use strict";

let IDV = window.IDV || {};

IDV.Track = (function () {
  let my = {};

  let loadingStart = new Event('loading_start');
  let loadingStop = new Event('loading_stop');

  let getTrackingEvents = function (form, successHandler, failHandler) {
    document.dispatchEvent(loadingStart);
    let queryParams = "?label_id=" + form.querySelectorAll('[name=label_id]')[0].value;
    fetch(form.getAttribute('action') + queryParams, {
      credentials: 'same-origin',
      method: 'GET',
    }).then(async function (response) {
      if (response.ok) {
        successHandler(await response.text())
      }
      else {
        let jsonResponse = await response.json();
        failHandler(jsonResponse.message);
      }
    }).catch(function (response) {
      failHandler(response.body);
    }).finally(function () {
      document.dispatchEvent(loadingStop);
    });
  };

  let successHandler = function (responseBody) {
    let eventsPanel = document.getElementById('events');
    eventsPanel.innerHTML = responseBody;
    eventsPanel.classList.remove('hidden');
  };

  let failHandler = function (message) {
    let errorMsg = document.getElementById('tracking-error');
    errorMsg.innerHTML = message;
    showErrors(errorMsg);
  };

  let showErrors = function (errorContainer) {
    errorContainer.parentElement.classList.add('has-error');
    errorContainer.classList.remove('hidden');
    document.getElementById('events').classList.add('hidden');
  };

  let hideErrors = function (errorContainer) {
    errorContainer.parentElement.classList.remove('has-error');
    errorContainer.classList.add('hidden');
  };

  my.labelExists = function () {
    return document.getElementById('tracking-number').value.length !== 0;
  };

  my.submit = function () {
    let trackingForm = document.getElementById('get-tracking-events');
    let errorMsg = document.getElementById('tracking-error');

    hideErrors(errorMsg);
    getTrackingEvents(trackingForm, successHandler, failHandler);
  };

  my.init = function () {
    document.getElementById('get-tracking-events').onsubmit = function (event) {
      event.preventDefault();
      my.submit();
    };

    document.getElementById('track-parcel').onclick = function (event) {
      event.preventDefault();
      my.submit();
    };
  };

  return my;
})();

IDV.Spinner = (function () {
  let my = {},
    target = null,
    spinner = null,
    opts = null;

  my.init = function (event_start, event_stop) {
    // Spinner options
    target = document.getElementById('spinner-container');
    opts = {
      lines: 13, // The number of lines to draw
      length: 10, // The length of each line
      width: 4, // The line thickness
      radius: 11, // The radius of the inner circle
      corners: 1, // Corner roundness (0..1)
      rotate: 0, // The rotation offset
      direction: 1, // 1: clockwise, -1: counterclockwise
      color: '#737B81', // #rgb or #rrggbb or array of colors
      speed: 1.2, // Rounds per second
      trail: 48, // Afterglow percentage
      shadow: false, // Whether to render a shadow
      hwaccel: false, // Whether to use hardware acceleration
      className: 'spinner', // The CSS class to assign to the spinner
      zIndex: 2e9, // The z-index (defaults to 2000000000)
      top: '50%', // Top position relative to parent in px
      left: '50%' // Left position relative to parent in px
    };

    document.addEventListener(event_start, function (e) {
      spinner = new Spinner(opts).spin(target);
    });

    document.addEventListener(event_stop, function (e) {
      spinner.stop();
    });
  };

  return my;
})();


document.addEventListener("DOMContentLoaded", function (event) {
  IDV.Track.init();
  IDV.Spinner.init('loading_start', 'loading_stop');

  if (IDV.Track.labelExists()) {
    IDV.Track.submit();
  }
});
