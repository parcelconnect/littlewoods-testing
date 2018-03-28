"use strict";

var IDV = window.IDV || {};

IDV.Track = (function() {
  var my = {},
      trackingForm = null,
      errorMsg = null;

  var getTrackingEvents = function($form, successHandler, failHandler) {
    $.ajax({
      url: $form.attr('action'),
      data: $form.serialize()
    })
    .done(successHandler)
    .fail(failHandler);
  }

  var successHandler = function(response) {
    var eventsPanel = $('#js-events');
    var recipientData = '';
    response.events.forEach(function (event){
      // not all scan events have recipient data
      if(event.recipient.address1 != ""){
        recipientData = event.recipient
      }
      // not all scan events have a contact name
      if(event.recipient.contactName){
        recipientData['contactName'] = event.recipient.contactName
      }
    })
    var templateHTML = $('#js-events-template').html();
    var template = _.template(templateHTML);
    var events_reverse_order = response.events.reverse();
    var eventsHTML = template({
      events: events_reverse_order,
      latestEvent: events_reverse_order[0],
      today: response.today,
      labelID: response.label_id,
      recipientData: recipientData
    });
    eventsPanel.html(eventsHTML);
    eventsPanel.removeClass('hidden');
  };

  var failHandler = function(response) {
    var errorMsg = $('#tracking-error');
    var errorObj = jQuery.parseJSON(response.responseText);
    errorMsg.html(errorObj.message);
    showErrors(errorMsg);
  };

  var showErrors = function(errorContainer) {
    errorContainer.parent().addClass('has-error');
    errorContainer.removeClass('hidden');
    $('#js-events').addClass('hidden');
  };

  var hideErrors = function(errorContainer) {
    errorContainer.parent().removeClass('has-error');
    errorContainer.addClass('hidden');
  };

  my.labelExists = function() {
    return $('#tracking-number').val().length !== 0;
  }

  my.submit = function() {
    var $trackingForm = $('#js-get-tracking-events');
    var $errorMsg = $('#tracking-error');

    hideErrors($errorMsg);
    getTrackingEvents($trackingForm, successHandler, failHandler);
  };

  my.init = function() {
    $('#js-get-tracking-events').submit(function(event) {
      event.preventDefault();
      my.submit();
    });

     $('#track-parcel').click(function(event) {
      event.preventDefault();
      my.submit();
    });
  }

  return my;
})();

IDV.Spinner = (function() {
  var my = {},
      target = null,
      spinner = null,
      opts = null;

  my.init = function() {
    // Spinner options
    target = $('#spinner-container');
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

    $(document).ajaxStart(function () {
      spinner = new Spinner(opts).spin();
      target.append(spinner.el);
    });

    $(document).ajaxStop(function () {
      spinner.stop();
    });
  }

  return my;
})();

/*
 * Entry point.
 */
$(function() {
  IDV.Track.init();
  IDV.Spinner.init();

  if (IDV.Track.labelExists()) {
    IDV.Track.submit();
  }
});
