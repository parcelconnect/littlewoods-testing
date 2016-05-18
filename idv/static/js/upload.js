"use strict";

var IDV = window.IDV || {};
var Django = window.Django || {};

/*
 * Responsible for keeping track of the files to be uploaded.
 */
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

/*
 * Adds and updates upload progress bars.
 */
IDV.ProgressBars = (function() {
  var my = {};
  var containerID = 'progress-bars';
  var progressBarTemplateContainerID = 'progress-bar-template-container';
  var $container = null;

  my.reset = function() {
    $container.html('');
  };

  var add = function(file) {
    var $templateContainer = $('#'+progressBarTemplateContainerID).clone();
    $templateContainer.find('.filename').html(file.name);
    $templateContainer.find('.progress-bar').attr('data-filename', file.name)
    var $bar = $templateContainer.children();
    $container.append($bar);
  };

  my.addMany = function(files) {
    var bar = null;
    $.each(files, function(idx, file) {
      add(file);
    });
  };

  my.update = function(xhr, file) {
    xhr.upload.addEventListener("progress", function(evt) {
      if (evt.lengthComputable) {
        var percentComplete = evt.loaded / evt.total;
        percentComplete = parseInt(percentComplete * 100);
        $container.find('[data-filename="'+file.name+'"]')
          .css('width', percentComplete+'%')
          .attr('aria-valuenow', percentComplete);
        if (percentComplete == 100) {
          $('.progress-bar').addClass('progress-bar-success');
        };
      }
    }, false);
  };

  my.init = function() {
    $container = $('#'+containerID);
  };

  return my;
})();

/*
 * Your entry module.
 */
IDV.UploadForm = (function() {
  var my = {};
  var formID = 'id-docs';
  var $form = null;
  var fileHolder = null;
  var progressBars = null;

  var uploadFile = function(file, signed_url) {
    $.ajax({
      url: signed_url,
      type: "PUT",
      data: file,
      contentType: file.type,
      processData: false,
      xhr: function() {
        var xhr = new window.XMLHttpRequest();
        progressBars.update(xhr, file);
        return xhr;
      }
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
    fileHolder.reset();
    progressBars.reset();

    var files = getFormFiles();
    fileHolder.addFiles(files);
    progressBars.addMany(files);

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
    progressBars = IDV.ProgressBars;
    progressBars.init();

    fileHolder = IDV.FileHolder;
    fileHolder.removeFile("asdf");

    $form = $('#'+formID);
    $form.submit(submitHandler)
  };
  return my;
})();

/*
 * Entry point.
 */
$(function() {
  IDV.UploadForm.init();
});
