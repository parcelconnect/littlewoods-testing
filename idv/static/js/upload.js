"use strict";

var IDV = window.IDV || {};
var Django = window.Django || {};

IDV.FormUtils = (function() {
  var my = {};
  var errorClass = 'has-error';
  var errorListClass = 'error-list';

  var createErrorList = function(errors) {
    var $errorList = $('<ul class="' + errorListClass + '"></ul>');
    $.each(errors, function(idx, error) {
      $errorList.append('<li>' + error + '</li>');
    });
    return $errorList;
  }

  my.fieldHasError = function(element) {
    $(element).closest('.form-group').hasClass(errorClass);
  }

  my.addFieldErrors = function(element, errors) {
    $(element).closest('.form-group').addClass(errorClass);
    var $errorList = createErrorList(errors);
    $(element).after($errorList);
  }

  my.clearFieldErrors = function(element) {
    $(element).closest('.form-group').removeClass(errorClass);
    $(element).siblings('.' + errorListClass).remove();
  }

  my.clearErrors = function() {
    $('.form-group').removeClass(errorClass);
    $('.'+errorListClass).remove();
  }

  my.focusOnFirstErrorInput = function() {
    var firstErrorContainer = $('.form-group.' + errorClass)[0];
    var firstErrorInput = $(firstErrorContainer).find('input')[0];
    $(firstErrorInput).focus();
  }

  return my;
})();

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
    .fail(function(jqXHR, textStatus, error) {
      if (typeof Raven !== 'undefined') {
        Raven.captureMessage('Error uploading Photo ID file', {
          extra: {status: jqXHR.status, response: jqXHR.response}
        });
      } else {
        console.log(JSON.stringify({status: jqXHR.status, response: jqXHR.response}))
      }
      uploadFileFailHandler(file);
    });
  };

  var showUploadSuccessMessage = function() {
    var content = $('#successful-upload-template').html();
    $('#content-wrapper').html(content)
  };

  var uploadFileDoneHandler = function(file) {
    fileHolder.removeFile(file);
    if (fileHolder.isEmpty()) {
      showUploadSuccessMessage();
    };
  };

  var uploadFileFailHandler = function(file) {
    var content = $('#failed-upload-template').html();
    $('#js-modal .modal-content').html(content);
    $('#js-modal').modal('show');
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

  var failedSignHandler = function(jqXHR) {
    if (jqXHR.status !== 400) {
      var error_msg = 'Unexpected response when submitting id verification form: status ' + jqXHR.status;
      if (typeof Raven !== 'undefined') {
        Raven.captureMessage(error_msg, {
          extra: {status: jqXHR.status, response: jqXHR.responseText}
        });
      } else {
        console.log(error_msg);
        console.log(JSON.stringify({status: jqXHR.status, response: jqXHR.responseText}));
      }
      uploadFileFailHandler();
      return;
    }

    var errors = jqXHR.responseJSON.errors;
    for (var fieldName in errors) {
      var $field = $('input[name="' + fieldName + '"]');
      var fieldErrors = errors[fieldName];
      IDV.FormUtils.addFieldErrors($field, fieldErrors);
    }
    IDV.FormUtils.focusOnFirstErrorInput();
  };

  var getFormFiles = function() {
    /* There is only one file input */
    var $fileInput = $form.find('input[type="file"]')[0];
    return $fileInput.files;
  };

  var submitHandler = function(event) {
    event.preventDefault();
    IDV.FormUtils.clearErrors();
    fileHolder.reset();
    progressBars.reset();

    var files = getFormFiles();
    fileHolder.addFiles(files);
    progressBars.addMany(files);

    var data = {
      email: $('#lwi-email-address').val(),
      account_number: $('#lwi-account-number').val(),
      file_data: fileHolder.stringifyForSigning()
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

  var $requiredFields = $(':input[required=""],:input[required]');
  $requiredFields.keydown(function() {
    IDV.FormUtils.clearFieldErrors(this);
  });
});
