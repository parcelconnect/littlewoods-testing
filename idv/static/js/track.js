"use strict";

var IDV = window.IDV || {};

IDV.Track = (function() {
  var my = {},
      trackingForm = null;

  var getTrackingEvents = function($form, successHandler, failHandler) {
    return $.ajax({
      url: $form.attr('action'),
      data: $form.serialize(),
    })
    .done(successHandler)
    .fail(failHandler);
  }

  var successHandler = function(response) {
    var errorMsg = $('#tracking-error');
    var eventsPanel = $('#js-events');
    var templateHTML = $('#js-events-template').html();
    var template = _.template(templateHTML)
    var eventsHTML = template({
      events: response.events,
      latestEvent: response.events[0],
      today: response.today,
      labelID: response.label_id
    });
    eventsPanel.html(eventsHTML);
    eventsPanel.removeClass('hidden');
    errorMsg.parent().removeClass('has-error');
    errorMsg.addClass('hidden');
  };

  var failHandler = function(response) {
    var errorMsg = $('#tracking-error');
    var errorObj = jQuery.parseJSON(response.responseText);
    errorMsg.html(errorObj.message);
    errorMsg.parent().addClass('has-error');
    errorMsg.removeClass('hidden');
    $('#js-events').addClass('hidden');
  };

  my.init = function() {
    var $trackingForm = $('#js-get-tracking-events');

    $trackingForm.submit(function() {
      event.preventDefault();
      getTrackingEvents($(this), successHandler, failHandler);
    });

     $('#track-parcel').click(function() {
      event.preventDefault();
      getTrackingEvents($trackingForm, successHandler, failHandler);
    });
  }

  return my;
})();

/*
 * Entry point.
 */
$(function() {
  IDV.Track.init();
});
