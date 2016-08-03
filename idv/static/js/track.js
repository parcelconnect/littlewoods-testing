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
    var templateHTML = $('#js-events-template').html();
    var template = _.template(templateHTML)
    var eventsHTML = template({
      events: response.events,
      latestEvent: response.events[0],
      today: response.today,
      labelID: response.label_id
    });
    $('#js-events').html(eventsHTML);
  };

  var failHandler = function(response) {
    console.log("fail");
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
