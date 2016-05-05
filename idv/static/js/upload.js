"use strict";

var IDV = window.IDV || {};
var Django = window.Django || {};

IDV.FileHolder = (function() {
  var my = {};
  /* filename -> file object */
  var _files = {};

  my.reset = function() {
    _files = {};
  };

  my.addFiles = function(files) {
    $.each(files, function(idx, file) {
      _files[file.name] = file;
    });
  }

  my.removeFile = function(file) {
    delete _files[file.name];
  };

  my.isEmpty = function() {
    return $.isEmptyObject(_files);
  };

  my.get = function(filename) {
    return _files[filename];
  };

  my.stringifyForSigning = function() {
    var filenameToFiletype = {};
    $.each(_files, function(filename, file) {
      filenameToFiletype[filename] = file.type;
    });
    var stringified = JSON.stringify(filenameToFiletype);
    return encodeURIComponent(stringified);
  };

  return my;
})();

IDV.UploadForm = (function() {
  var my = {};
  var formID = 'id-docs';
  var $form = null;
  var fileHolder = null;

  var uploadFile = function(file, signed_url) {
    $.ajax({
      url: signed_url,
      type: "PUT",
      data: file,
      contentType: file.type,
      processData: false,
    })
    .done(function() {
      uploadFileDoneHandler(file);
    })
    .fail(function() {
      uploadFileFailHandler(file);
    });
  };

  var showUploadSuccessMessage = function() {
    $('#js-success-message').modal('show');
    console.log("All files have been uploaded");
  };

  var uploadFileDoneHandler = function(file) {
    fileHolder.removeFile(file);
    if (fileHolder.isEmpty()) {
      showUploadSuccessMessage();
    };
  };

  var uploadFileFailHandler = function(file) {
    console.log("Could not upload " + file.name);
  };

  var getSignedRequests = function(data, handlers) {
    $.ajax({
      url: Django.Data.get('sign_s3_request_url'),
      method: 'GET',
      data: data,
      dataType: 'json'
    })
    .done(handlers.done)
    .fail(handlers.fail);
  };

  var uploadFiles = function(response) {
    $.each(response, function(filename, signed_url) {
      var file = fileHolder.get(filename);
      uploadFile(file, signed_url);
    });
  };

  var failedSignHandler = function() {
    console.log("Could not sign request.");
  };

  var getFormFiles = function() {
    /* There is only one file input */
    var $fileInput = $form.find('input[type="file"]')[0];
    return $fileInput.files;
  };

  var submitHandler = function(event) {
    event.preventDefault();
    var files = getFormFiles();
    fileHolder.reset();
    fileHolder.addFiles(files);

    var data = {
      email: $('#lwi-email-address').val(),
      account: $('#lwi-account-number').val(),
      fileData: fileHolder.stringifyForSigning()
    };
    var handlers = {
      done: uploadFiles,
      fail: failedSignHandler,
    };
    getSignedRequests(data, handlers);
  };

  my.init = function() {
    fileHolder = IDV.FileHolder;
    fileHolder.removeFile("asdf");
    $form = $('#'+formID);
    $form.submit(submitHandler)
  };
  return my;
})();

$(function() {
  IDV.UploadForm.init();
});
