"use strict";

var IDV = window.IDV || {};
var Django = window.Django || {};

IDV.UploadForm = (function() {
  var my = {};
  var formID = 'id-docs';
  var $form = null;
  var filenamesToBeUploaded = [];

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

  var addFileToUploadList = function(file) {
    filenamesToBeUploaded.push(file.name);
  };

  var removeFileFromUploadList = function(file) {
    var idx = filenamesToBeUploaded.indexOf(file.name);
    filenamesToBeUploaded.splice(idx, 1);
  };

  var isUploadListEmpty = function() {
    return filenamesToBeUploaded.length == 0;
  };

  var showUploadSuccessMessage = function() {
    $('#js-success-message').modal('show');
    console.log("All files have been uploaded");
  };

  var uploadFileDoneHandler = function(file) {
    removeFileFromUploadList(file);
    if (isUploadListEmpty()) {
      showUploadSuccessMessage();
    };
  };

  var uploadFileFailHandler = function(file) {
    console.log("Could not upload " + file.name);
  };

  var getSignedRequests = function(files, doneHandler, failHandler) {
    var filenameToFiletype = {};
    var filenameToFile = {};
    $.each(files, function(idx, file) {
      filenameToFiletype[file.name] = file.type;
      filenameToFile[file.name] = file;
    });
    var fileData = encodeURIComponent(JSON.stringify(filenameToFiletype));

    $.ajax({
      url: Django.Data.get('sign_s3_request_url'),
      method: 'GET',
      data: {fileData: fileData},
      dataType: 'json'
    })
    .done(function(response) {
      doneHandler(response, filenameToFile);
    })
    .fail(failHandler);
  };

  var getSignedRequestsDoneHandler = function(response, filenameToFile) {
    $.each(response, function(filename, signed_url) {
      var file = filenameToFile[filename];
      addFileToUploadList(file);
      uploadFile(file, signed_url);
    });
  };

  var getSignedRequestsFailHandler = function() {
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
    getSignedRequests(
      files,
      getSignedRequestsDoneHandler,
      getSignedRequestsFailHandler
    );
  };

  my.init = function() {
    $form = $('#'+formID);
    $form.submit(submitHandler)
  };
  return my;
})();

$(function() {
  IDV.UploadForm.init();
});
